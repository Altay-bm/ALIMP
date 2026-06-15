from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from templates_env import templates
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
router = APIRouter()

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/auth/login')
def get_login(request: Request):
    return templates.TemplateResponse(request, 'login.html', { 'request': request })

@router.post('/auth/login')
async def post_login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.password_hash):
        return templates.TemplateResponse(request, 'login.html', { 'request': request, 'error': 'Неверный логин или пароль' })
    request.session['user_id'] = user.id
    return RedirectResponse(url='/requests', status_code=303)

@router.get('/auth/logout')
def do_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url='/login')
