from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas import ContactSchema

from validate_email import validate_email

from datetime import datetime, timedelta


async def get_contacts(offset: int, limit: int, db: AsyncSession):
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession):
    contact = Contact(**body.model_dump(exclude_unset=True))
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactSchema, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contacts(field_search, offset: int, limit: int, db: AsyncSession):
    if validate_email(field_search):
        stmt = (
            select(Contact)
            .where(Contact.email == field_search)
            .offset(offset)
            .limit(limit)
        )
        contacts = await db.execute(stmt)
    else:
        stmt = (
            select(Contact)
            .where(
                or_(
                    Contact.name.like(f"%{field_search}%"),
                    (Contact.phone.like(f"%{field_search}%")),
                )
            )
            .offset(offset)
            .limit(limit)
        )
        contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def search_contacts_coming_birthday(offset: int, limit: int, db: AsyncSession):
    today = datetime.now().date()
    end_date = today + timedelta(days=7)
    stmt = (
        select(Contact)
        .filter(Contact.birthday.between(today, end_date))
        .offset(offset)
        .limit(limit)
    )
    contacts = await db.execute(stmt)
    return contacts.scalars().all()
