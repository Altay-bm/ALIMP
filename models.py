from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from enum import Enum

Base = declarative_base()

class RoleEnum(str, Enum):
    manager = 'manager'
    engineer = 'engineer'
    admin = 'admin'

class StatusEnum(str, Enum):
    new = 'Новая'
    pending = 'На согласовании'
    in_work = 'В работе (проектирование)'
    done = 'Выполнена'
    shipped = 'Отгружена'

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)

    created_requests = relationship('Request', back_populates='created_by', foreign_keys='Request.created_by_id')
    assigned_requests = relationship('Request', back_populates='assigned_to', foreign_keys='Request.assigned_to_id')

class Request(Base):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True)
    number = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    client_name = Column(String, nullable=False)
    client_contact = Column(String, nullable=True)
    client_phone = Column(String, nullable=True)
    client_email = Column(String, nullable=True)

    equipment_type = Column(String, nullable=False)
    equipment_params = Column(Text, nullable=True)
    quantity = Column(Integer, default=1)

    status = Column(String, default=StatusEnum.new.value)
    price = Column(DECIMAL(12,2), nullable=True)

    assigned_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    assigned_to = relationship('User', foreign_keys=[assigned_to_id])
    created_by = relationship('User', foreign_keys=[created_by_id])

    comments = relationship('Comment', back_populates='request', cascade='all, delete-orphan')
    history = relationship('History', back_populates='request', cascade='all, delete-orphan')

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    author = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    request_id = Column(Integer, ForeignKey('requests.id'))

    request = relationship('Request', back_populates='comments')

class History(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('requests.id'))
    author = Column(String, nullable=False)
    action = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    request = relationship('Request', back_populates='history')
