from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy.orm import Session
from templates_env import templates
from database import SessionLocal
from models import Request as ReqModel, StatusEnum, User
from datetime import datetime
from sqlalchemy import extract, func

router = APIRouter()

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    return db.get(User, user_id)

@router.get('/reports')
def reports_get(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    # simple statistics
    stats = {}
    for s in StatusEnum:
        stats[s.value] = db.query(func.count(ReqModel.id)).filter(ReqModel.status == s.value).scalar()
    return templates.TemplateResponse(request, 'reports.html', { 'request': request, 'stats': stats, 'user': user })

@router.post('/reports')
def reports_post(request: Request, year: int = Form(...), month: int = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    # total sum of shipped in month
    total = db.query(func.coalesce(func.sum(ReqModel.price),0)).filter(ReqModel.status == 'Отгружена', extract('year', ReqModel.created_at) == year, extract('month', ReqModel.created_at) == month).scalar()
    stats = {}
    for s in StatusEnum:
        stats[s.value] = db.query(func.count(ReqModel.id)).filter(ReqModel.status == s.value).scalar()
    return templates.TemplateResponse(request, 'reports.html', { 'request': request, 'stats': stats, 'total': total, 'year': year, 'month': month, 'user': user })
