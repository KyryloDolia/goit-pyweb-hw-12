from typing import List, Optional
from sqlalchemy import or_, func, and_
from sqlalchemy.orm import Session
from src.database.models import Contact
from src.schemas import ContactCreate, ContactUpdate
from datetime import datetime, date, timedelta

async def get_contacts(skip: int, limit: int, user_id: int, db: Session) -> List[Contact]:
    return db.query(Contact).filter(Contact.user_id == user_id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user_id: int, db: Session) -> Optional[Contact]:
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user_id)).first()


async def create_contact(body: ContactCreate, user_id: int, db: Session) -> Contact:
    contact = Contact(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        phone=body.phone,
        birthday=body.birthday,
        user_id=user_id
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdate, user_id: int, db: Session) -> Optional[Contact]:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user_id)).first()
    if contact:
        for key, value in body.dict(exclude_unset=True).items():
            setattr(contact, key, value)
        db.commit()
        db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, user_id: int, db: Session) -> Optional[Contact]:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user_id)).first()
    if contact:
        db.delete(contact)
        db.commit()
        return contact
    return None


async def search_contacts(query: str, user_id: int, db: Session) -> List[Contact]:
    return db.query(Contact).filter(
        and_(
            Contact.user_id == user_id,
            or_(
                Contact.first_name.ilike(f"%{query}%"),
                Contact.last_name.ilike(f"%{query}%"),
                Contact.email.ilike(f"%{query}%"),
            )
        )
    ).all()


async def get_upcoming_birthdays(user_id: int, db: Session) -> List[Contact]:
    today = datetime.today().date()
    next_week = today + timedelta(days=7)

    # Extract only contacts with a birthday in the next 7 days
    contacts = db.query(Contact).filter(
        Contact.user_id == user_id,
        Contact.birthday.isnot(None),
        func.date_part('doy', Contact.birthday) >= func.date_part('doy', today),
        func.date_part('doy', Contact.birthday) <= func.date_part('doy', next_week)
    ).all()

    # Adjust for weekends
    for contact in contacts:
        birthday_this_year = contact.birthday.replace(year=today.year)
        if birthday_this_year < today:
            birthday_this_year = birthday_this_year.replace(year=today.year + 1)
        contact.congratulation_date = adjust_for_weekend(birthday_this_year)

    return contacts


def adjust_for_weekend(date: date) -> date:
    if date.weekday() == 5:
        return date + timedelta(days=2)
    elif date.weekday() == 6:
        return date + timedelta(days=1)
    else:
        return date
