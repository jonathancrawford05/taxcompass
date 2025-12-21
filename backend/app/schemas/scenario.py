"""
Pydantic schemas for Tax Scenarios
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from decimal import Decimal
from uuid import UUID


class ScenarioCreate(BaseModel):
    """Schema for creating a scenario"""

    analysis_id: UUID
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    parameters: Dict = Field(..., description="Scenario parameters (what changed)")


class ScenarioUpdate(BaseModel):
    """Schema for updating a scenario"""

    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    parameters: Optional[Dict] = None


class ScenarioCalculation(BaseModel):
    """Tax calculation results for a scenario"""

    origin_tax: Decimal
    destination_tax: Decimal
    departure_tax: Optional[Decimal] = None
    total_tax: Decimal
    after_tax_income: Decimal
    effective_rate: float
    three_year_impact: Optional[Decimal] = None


class ScenarioResponse(BaseModel):
    """Schema for scenario in API responses"""

    id: UUID
    analysis_id: UUID
    name: str
    description: Optional[str]
    parameters: Dict

    # Tax calculations
    origin_tax: Optional[Decimal]
    destination_tax: Optional[Decimal]
    departure_tax: Optional[Decimal]
    total_tax: Optional[Decimal]
    after_tax_income: Optional[Decimal]
    effective_rate: Optional[float]
    three_year_impact: Optional[Decimal]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
