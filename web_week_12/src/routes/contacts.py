from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas import ContactResponse, ContactCreate, ContactUpdate
from src.repository import contacts as repo_contacts
from src.services.auth import auth_service
from src.database.models import User

router = APIRouter(prefix='/contacts', tags=["contacts"])

@router.get('/', response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    contacts = await repo_contacts.get_contacts(skip, limit, current_user.id, db)
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    contact = await repo_contacts.get_contact(contact_id, current_user.id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    return await repo_contacts.create_contact(body, current_user.id, db)

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactUpdate,
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    contact = await repo_contacts.update_contact(contact_id, body, current_user.id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    contact = await repo_contacts.remove_contact(contact_id, current_user.id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    contacts = await repo_contacts.search_contacts(query, current_user.id, db)
    return contacts

@router.get("/upcoming-birthdays/", response_model=List[ContactResponse])
async def upcoming_birthdays(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    contacts = await repo_contacts.get_upcoming_birthdays(current_user.id, db)
    return contacts