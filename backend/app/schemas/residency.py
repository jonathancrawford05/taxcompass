"""
Pydantic schemas for Residency Analysis
Based on the plan in project_4_tax_agent_plan.md
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Literal
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


class UserProfile(BaseModel):
    """User's tax situation profile - input for analysis"""

    # Personal
    citizenship: List[str] = Field(..., description="List of citizenship countries (ISO codes)")
    current_country: str = Field(..., description="Current country of residence (ISO code)")
    destination_country: str = Field(..., description="Destination country (ISO code)")
    departure_date: date = Field(..., description="Planned departure date")

    # Family
    marital_status: Literal["single", "married", "common_law"]
    has_spouse: bool
    spouse_location: Optional[str] = None  # Country code
    has_dependents: bool
    dependents_location: Optional[str] = None  # Country code

    # Property
    owns_home_origin: bool
    home_disposition: Optional[Literal["sell", "rent", "keep_vacant"]] = None
    owns_home_destination: bool = False

    # Employment
    employment_type: Literal["employee", "self_employed", "business_owner"]
    employer_country: str = Field(..., description="Country where employer is located")
    annual_income: Decimal = Field(..., description="Annual income in USD")

    # Financial
    has_rental_property: bool = False
    investment_accounts_balance: Optional[Decimal] = None
    rrsp_balance: Optional[Decimal] = None  # Canada-specific
    tfsa_balance: Optional[Decimal] = None  # Canada-specific
    unrealized_capital_gains: Optional[Decimal] = None

    # Ties (for scoring)
    ties_score: Dict[str, int] = Field(default_factory=dict)

    @field_validator('annual_income', 'investment_accounts_balance',
                    'rrsp_balance', 'tfsa_balance', 'unrealized_capital_gains')
    @classmethod
    def validate_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount must be non-negative')
        return v


class ResidencyAnalysis(BaseModel):
    """Output from residency analyzer agent"""

    origin_status: Literal["resident", "non-resident", "factual-resident", "deemed-resident"]
    destination_status: Literal["resident", "non-resident"]
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    reasoning: str = Field(..., description="Detailed reasoning for determination")
    key_factors: List[str] = Field(..., description="Key factors in determination")
    red_flags: List[str] = Field(default_factory=list, description="Warning items to address")
    recommendations: List[str] = Field(..., description="Actionable recommendations")


class TaxCalculation(BaseModel):
    """Tax calculation for a scenario"""

    scenario_name: str
    origin_tax: Decimal
    destination_tax: Decimal
    departure_tax: Optional[Decimal] = None
    total_tax: Decimal
    after_tax_income: Decimal
    effective_rate: float = Field(..., description="Effective tax rate as percentage")


class ScenarioComparison(BaseModel):
    """Comparison of multiple tax scenarios"""

    baseline: TaxCalculation
    scenarios: List[TaxCalculation]
    best_scenario: str
    worst_scenario: str
    savings_vs_worst: Decimal
    three_year_impact: Decimal


class ActionPlan(BaseModel):
    """Actionable recommendations and timeline"""

    priority_actions: List[str]
    timeline: Dict[str, List[str]] = Field(
        ...,
        description="Timeline dict with keys like '3_months_before', '1_month_before', etc."
    )
    forms_to_file: List[str]
    documents_needed: List[str]
    professional_help_needed: bool
    professional_help_reason: Optional[str] = None
    estimated_cost: Dict[str, Decimal] = Field(
        ...,
        description="Breakdown of one-time costs"
    )


class AnalysisCreate(BaseModel):
    """Schema for creating a new analysis"""

    title: Optional[str] = None
    origin_country: str = Field(..., min_length=2, max_length=2)
    destination_country: str = Field(..., min_length=2, max_length=2)
    departure_date: date
    user_profile: UserProfile


class AnalysisResponse(BaseModel):
    """Schema for analysis in API responses"""

    id: UUID
    user_id: UUID
    title: Optional[str]
    origin_country: str
    destination_country: str
    departure_date: date
    status: str

    # Results (only present when analysis is complete)
    origin_residency_status: Optional[str] = None
    destination_residency_status: Optional[str] = None
    confidence_score: Optional[float] = None
    key_factors: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    red_flags: Optional[List[str]] = None
    reasoning: Optional[str] = None

    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnalysisRunRequest(BaseModel):
    """Request to run analysis"""

    run_scenarios: bool = Field(
        default=False,
        description="Whether to also run scenario comparisons"
    )
    scenario_count: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Number of scenarios to compare (1-5)"
    )
