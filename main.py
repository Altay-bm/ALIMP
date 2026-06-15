from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from templates_env import templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Request as ReqModel, Comment, History, StatusEnum
from passlib.context import CryptContext
from config import SECRET_KEY, EQUIPMENT_CATALOG
from datetime import datetime
import uuid

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount('/static', StaticFiles(directory='static'), name='static')

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create DB
Base.metadata.create_all(bind=engine)

# Initial users
from sqlalchemy import select

def init_users():
    db = SessionLocal()
    try:
        stmt = select(User).where(User.username.in_(['manager','engineer','admin']))
        existing = db.execute(stmt).scalars().all()
        if not existing:
            users = [
                { 'name':'Менеджер','username':'manager','password':'man123','role':'manager'},
                { 'name':'Инженер','username':'engineer','password':'eng123','role':'engineer'},
                { 'name':'Администратор','username':'admin','password':'admin123','role':'admin'},
            ]
            for u in users:
                user = User(name=u['name'], username=u['username'], password_hash=pwd_context.hash(u['password']), role=u['role'])
                db.add(user)
            db.commit()
    finally:
        db.close()

init_users()

# Auth helpers
def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    return db.get(User, user_id)

def require_role(request: Request, roles):
    def _dep(user: User = Depends(get_current_user)):
        if not user or user.role not in roles:
            raise RedirectResponse(url='/login')
        return user
    return _dep

# Utils
from sqlalchemy import func

def generate_request_number(db: Session):
    today = datetime.utcnow().strftime('%Y%m%d')
    prefix = f"РЗА-{today}"
    # count existing today
    count = db.query(func.count(ReqModel.id)).filter(ReqModel.number.like(f"{prefix}%")).scalar() or 0
    return f"{prefix}-{count+1:04d}"

# Routes
@app.get('/', response_class=RedirectResponse)
def index():
    return '/requests'

@app.get('/login')
def login_get(request: Request):
    return templates.TemplateResponse(request, 'login.html', { 'request': request })

@app.post('/login')
async def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.password_hash):
        return templates.TemplateResponse(request, 'login.html', { 'request': request, 'error': 'Неверный логин или пароль' })
    request.session['user_id'] = user.id
    return RedirectResponse(url='/requests', status_code=303)

@app.get('/logout')
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url='/login')

# Include routers implemented in separate files
from routers import requests_router, users_router, reports_router, auth_router
app.include_router(auth_router)
app.include_router(requests_router)
app.include_router(users_router)
app.include_router(reports_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
