"""
Authentication utilities
Temporary simple auth for development - replace with proper OAuth in production
"""
from typing import Optional
from uuid import UUID, uuid4
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user

    For development: Creates a demo user if no auth provided
    In production: This should validate JWT tokens
    """
    # For development: auto-create demo user
    # In production, replace with proper JWT validation

    demo_email = "demo@taxcompass.io"

    # Check if demo user exists
    user = db.query(User).filter(User.email == demo_email).first()

    if not user:
        # Create demo user
        user = User(
            email=demo_email,
            full_name="Demo User",
            is_active=True,
            tier="free"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user
    Raises HTTPException if user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user
