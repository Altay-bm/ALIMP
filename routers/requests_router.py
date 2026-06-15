from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Request as ReqModel, User, Comment, History, StatusEnum
from config import EQUIPMENT_CATALOG
from datetime import datetime
from sqlalchemy import or_
from templates_env import templates

router = APIRouter()

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth helpers
def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    return db.get(User, user_id)

# List requests
@router.get('/requests')
def list_requests(request: Request, status: str = None, q: str = None, client: str = None, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    query = db.query(ReqModel)
    if status:
        query = query.filter(ReqModel.status == status)
    if q:
        query = query.filter(ReqModel.number.ilike(f"%{q}%"))
    if client:
        query = query.filter(ReqModel.client_name.ilike(f"%{client}%"))
    items = query.order_by(ReqModel.created_at.desc()).all()
    return templates.TemplateResponse(request, 'requests_list.html', { 'request': request, 'items': items, 'user': user, 'statuses': [s.value for s in StatusEnum] })

@router.get('/requests/create')
def create_get(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role != 'manager':
        return RedirectResponse(url='/login')
    return templates.TemplateResponse(request, 'create_request.html', { 'request': request, 'equipment': EQUIPMENT_CATALOG, 'user': user })

@router.post('/requests/create')
async def create_post(request: Request,
                      client_name: str = Form(...), client_contact: str = Form(''), client_phone: str = Form(''), client_email: str = Form(''),
                      equipment_type: str = Form(...), equipment_params: str = Form(''), quantity: int = Form(1),
                      db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role != 'manager':
        return RedirectResponse(url='/login')
    # generate number
    from main import generate_request_number
    number = generate_request_number(db)
    req = ReqModel(number=number, client_name=client_name, client_contact=client_contact, client_phone=client_phone, client_email=client_email,
                   equipment_type=equipment_type, equipment_params=equipment_params, quantity=quantity, created_by_id=user.id)
    db.add(req)
    db.commit()
    # history
    h = History(request_id=req.id, author=user.name, action='Создание заявки')
    db.add(h)
    db.commit()
    return RedirectResponse(url=f'/requests/{req.id}', status_code=303)

@router.get('/requests/{req_id}')
def view_request(request: Request, req_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    req = db.get(ReqModel, req_id)
    if not req:
        return RedirectResponse(url='/requests')
    engineers = db.query(User).filter(User.role == 'engineer').all()
    return templates.TemplateResponse(request, 'request_detail.html', { 'request': request, 'item': req, 'user': user, 'equipment': EQUIPMENT_CATALOG, 'statuses': [s.value for s in StatusEnum], 'engineers': engineers })

@router.post('/requests/{req_id}/comment')
async def add_comment(request: Request, req_id: int, text: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ['engineer','admin']:
        return RedirectResponse(url='/login')
    req = db.get(ReqModel, req_id)
    if not req:
        return RedirectResponse(url='/requests')
    c = Comment(text=text, author=user.name, request_id=req.id)
    db.add(c)
    db.add(History(request_id=req.id, author=user.name, action='Добавлен комментарий'))
    db.commit()
    return RedirectResponse(url=f'/requests/{req.id}', status_code=303)

@router.post('/requests/{req_id}/status')
async def change_status(request: Request, req_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url='/login')
    req = db.get(ReqModel, req_id)
    if not req:
        return RedirectResponse(url='/requests')
    # Managers can edit until approved; engineers can set in_work/done; admin all
    allowed = False
    if user.role == 'admin':
        allowed = True
    elif user.role == 'engineer' and status in ["В работе (проектирование)", "Выполнена"]:
        allowed = True
    elif user.role == 'manager' and status != "Отгружена":
        allowed = True
    if not allowed:
        return RedirectResponse(url=f'/requests/{req.id}')
    req.status = status
    db.add(History(request_id=req.id, author=user.name, action=f'Смена статуса -> {status}'))
    db.commit()
    return RedirectResponse(url=f'/requests/{req.id}', status_code=303)

@router.post('/requests/{req_id}/assign')
async def assign_engineer(request: Request, req_id: int, engineer_id: int = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role not in ['manager','admin']:
        return RedirectResponse(url='/login')
    req = db.get(ReqModel, req_id)
    eng = db.get(User, engineer_id)
    if not req or not eng:
        return RedirectResponse(url=f'/requests/{req_id}')
    req.assigned_to_id = eng.id
    db.add(History(request_id=req.id, author=user.name, action=f'Назначен инженер {eng.name}'))
    db.commit()
    return RedirectResponse(url=f'/requests/{req.id}', status_code=303)

@router.post('/requests/{req_id}/edit')
async def edit_request(request: Request, req_id: int,
                       client_name: str = Form(...), client_contact: str = Form(''), client_phone: str = Form(''), client_email: str = Form(''),
                       equipment_type: str = Form(...), equipment_params: str = Form(''), quantity: int = Form(1), price: float = Form(None),
                       db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role != 'manager':
        return RedirectResponse(url='/login')
    req = db.get(ReqModel, req_id)
    if not req or req.status == 'Отгружена':
        return RedirectResponse(url=f'/requests/{req_id}')
    req.client_name = client_name
    req.client_contact = client_contact
    req.client_phone = client_phone
    req.client_email = client_email
    req.equipment_type = equipment_type
    req.equipment_params = equipment_params
    req.quantity = quantity
    if price:
        req.price = price
    db.add(History(request_id=req.id, author=user.name, action='Редактирование заявки'))
    db.commit()
    return RedirectResponse(url=f'/requests/{req.id}', status_code=303)
