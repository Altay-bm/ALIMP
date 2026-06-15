from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from passlib.context import CryptContext
from templates_env import templates

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
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

@router.get('/users')
def list_users(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role != 'admin':
        return RedirectResponse(url='/login')
    items = db.query(User).all()
    return templates.TemplateResponse(request, 'users_list.html', { 'request': request, 'items': items, 'user': user })

@router.post('/users/create')
async def create_user(request: Request, name: str = Form(...), username: str = Form(...), password: str = Form(...), role: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role != 'admin':
        return RedirectResponse(url='/login')
    u = User(name=name, username=username, password_hash=pwd_context.hash(password), role=role)
    db.add(u)
    db.commit()
    return RedirectResponse(url='/users', status_code=303)

@router.post('/users/{user_id}/delete')
def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role != 'admin':
        return RedirectResponse(url='/login')
    u = db.get(User, user_id)
    if u:
        db.delete(u)
        db.commit()
    return RedirectResponse(url='/users', status_code=303)

@router.post('/users/{user_id}/reset')
def reset_password(request: Request, user_id: int, new_password: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role != 'admin':
        return RedirectResponse(url='/login')
    u = db.get(User, user_id)
    if u:
        u.password_hash = pwd_context.hash(new_password)
        db.commit()
    return RedirectResponse(url='/users', status_code=303)
