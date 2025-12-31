"""
Clients Router
Handles client management endpoints.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.dependencies import get_current_user, require_manager_or_admin
from app.models.client import Client
from app.models.user import User

router = APIRouter(prefix="/api/clients", tags=["Clients"])


@router.get("", response_model=List[ClientResponse])
async def list_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all clients.
    All authenticated users can view clients.
    """
    clients = db.query(Client).order_by(Client.name).all()
    return [ClientResponse.from_orm_model(c) for c in clients]


@router.post("", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    Create a new client (managers and admins only).
    """
    # Check for duplicate email domain
    if client_data.email_domain:
        existing = db.query(Client).filter(Client.email_domain == client_data.email_domain).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Client with email domain '{client_data.email_domain}' already exists"
            )
    
    client = Client(
        name=client_data.name,
        email_domain=client_data.email_domain,
        contact_emails=client_data.contact_emails,
        industry=client_data.industry,
        account_manager_id=client_data.account_manager_id
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    
    return ClientResponse.from_orm_model(client)


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get client by ID.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return ClientResponse.from_orm_model(client)


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    Update client details (managers and admins only).
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check for duplicate email domain
    if client_data.email_domain and client_data.email_domain != client.email_domain:
        existing = db.query(Client).filter(
            Client.email_domain == client_data.email_domain,
            Client.id != client_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Client with email domain '{client_data.email_domain}' already exists"
            )
    
    # Apply updates
    if client_data.name:
        client.name = client_data.name
    if client_data.email_domain is not None:
        client.email_domain = client_data.email_domain
    if client_data.contact_emails is not None:
        client.contact_emails = client_data.contact_emails
    if client_data.industry is not None:
        client.industry = client_data.industry
    if client_data.account_manager_id is not None:
        client.account_manager_id = client_data.account_manager_id
    
    db.commit()
    db.refresh(client)
    
    return ClientResponse.from_orm_model(client)


@router.delete("/{client_id}")
async def delete_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    Delete a client (managers and admins only).
    Note: This will fail if client has associated escalations.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check for associated escalations
    if client.escalations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete client with existing escalations"
        )
    
    db.delete(client)
    db.commit()
    
    return {"message": "Client deleted successfully"}
