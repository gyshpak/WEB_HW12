from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, Security
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import (
    ContactSchema,
    ContactResponse,
    TokenSchema,
)
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service

from fastapi.security import (
    HTTPBearer,
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
)

router = APIRouter(prefix="/auth", tags=["auth"])
get_refresh_token = HTTPBearer()


@router.post(
    "/signup", response_model=ContactResponse, status_code=status.HTTP_201_CREATED
)
async def signup(body: ContactSchema, db: AsyncSession = Depends(get_db)):
    exist_user = await repository_contacts.get_contact_by_email(body.email, db)
    if exist_user:
        print(exist_user.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_contacts.create_contact(body, db)
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await repository_contacts.get_contact_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_contacts.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenSchema)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
    db: AsyncSession = Depends(get_db),
):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    contact = await repository_contacts.get_contact_by_email(email, db)
    if contact.refresh_token != token:
        await repository_contacts.update_token(contact, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_contacts.update_token(contact, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
