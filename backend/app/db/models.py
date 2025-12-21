"""
SQLAlchemy database models
Defines the database schema for TaxCompass
"""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.session import Base


class ResidencyStatus(str, enum.Enum):
    """Tax residency status options"""
    RESIDENT = "resident"
    NON_RESIDENT = "non-resident"
    DEEMED_RESIDENT = "deemed-resident"
    FACTUAL_RESIDENT = "factual-resident"


class AnalysisStatus(str, enum.Enum):
    """Analysis processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    """User account model"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    full_name = Column(String(255), nullable=True)

    # OAuth fields
    oauth_provider = Column(String(50), nullable=True)  # google, github, etc.
    oauth_id = Column(String(255), nullable=True)

    # Subscription/tier
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    tier = Column(String(50), default="free")  # free, pro, enterprise

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")


class Analysis(Base):
    """Tax residency analysis model"""
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Basic information
    title = Column(String(255), nullable=True)
    origin_country = Column(String(2), nullable=False)  # ISO country code
    destination_country = Column(String(2), nullable=False)
    departure_date = Column(DateTime, nullable=False)

    # User profile data (encrypted in production)
    user_profile = Column(JSON, nullable=False)  # Stores UserProfile schema

    # Analysis results
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    origin_residency_status = Column(SQLEnum(ResidencyStatus), nullable=True)
    destination_residency_status = Column(SQLEnum(ResidencyStatus), nullable=True)
    confidence_score = Column(Float, nullable=True)

    # Analysis outputs
    key_factors = Column(JSON, nullable=True)  # List of key determination factors
    recommendations = Column(JSON, nullable=True)  # List of recommendations
    red_flags = Column(JSON, nullable=True)  # List of warning items
    reasoning = Column(Text, nullable=True)  # Detailed reasoning

    # Agent metadata
    agent_trace_id = Column(String(255), nullable=True)  # For observability
    processing_time_seconds = Column(Float, nullable=True)

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="analyses")
    scenarios = relationship("Scenario", back_populates="analysis", cascade="all, delete-orphan")


class Scenario(Base):
    """Tax scenario comparison model"""
    __tablename__ = "scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False)

    # Scenario details
    name = Column(String(255), nullable=False)  # e.g., "Family moves together"
    description = Column(Text, nullable=True)

    # Scenario parameters (what changed from baseline)
    parameters = Column(JSON, nullable=False)

    # Tax calculations
    origin_tax = Column(Float, nullable=True)
    destination_tax = Column(Float, nullable=True)
    departure_tax = Column(Float, nullable=True)  # Canada departure tax
    total_tax = Column(Float, nullable=True)
    after_tax_income = Column(Float, nullable=True)
    effective_rate = Column(Float, nullable=True)

    # Multi-year projections
    three_year_impact = Column(Float, nullable=True)

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    analysis = relationship("Analysis", back_populates="scenarios")


class Document(Base):
    """Uploaded document model (for document ingestor agent)"""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=True)

    # File information
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, jpg, png
    file_size = Column(Integer, nullable=False)  # bytes
    file_path = Column(String(500), nullable=True)  # S3 path or local path

    # Processing
    is_processed = Column(Boolean, default=False)
    extracted_data = Column(JSON, nullable=True)  # Structured data from document
    processing_error = Column(Text, nullable=True)

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete


class AuditLog(Base):
    """Audit log for compliance and debugging"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Event details
    event_type = Column(String(100), nullable=False)  # login, analysis_created, etc.
    resource_type = Column(String(100), nullable=True)  # analysis, scenario, etc.
    resource_id = Column(UUID(as_uuid=True), nullable=True)

    # Request metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Event data
    event_data = Column(JSON, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
