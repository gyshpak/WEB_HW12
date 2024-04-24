from datetime import date
from sqlalchemy import Column, Integer, String, DateTime, func

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    phone: Mapped[str] = mapped_column(String(13), unique=True)
    birthday: Mapped[date] = mapped_column("birthday")
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
