"""
Database initialization script
Run this to create tables and initial data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.session import engine, Base
from app.db.models import User, Analysis, Scenario, Document, AuditLog


def init_db():
    """Create all tables in the database"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")


if __name__ == "__main__":
    init_db()
