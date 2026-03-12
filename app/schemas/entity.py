from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.models.entity import EntityStatus, LoanType


class EntityOnboardingStep1(BaseModel):
    """Step 1: Entity Details"""
    cin: str = Field(..., min_length=21, max_length=21, description="Corporate Identity Number")
    pan: str = Field(..., min_length=10, max_length=10, description="Permanent Account Number")
    name: str = Field(..., min_length=1, max_length=255, description="Entity Name")
    sector: str = Field(..., min_length=1, max_length=100, description="Industry Sector")
    turnover: float = Field(..., gt=0, description="Annual Turnover")
    
    @validator('cin')
    def validate_cin(cls, v):
        v = v.upper()
        if not v.isalnum():
            raise ValueError('CIN must be alphanumeric')
        return v
    
    @validator('pan')
    def validate_pan(cls, v):
        v = v.upper()
        if not v.isalnum():
            raise ValueError('PAN must be alphanumeric')
        return v


class EntityOnboardingStep2(BaseModel):
    """Step 2: Loan Details"""
    loan_type: Optional[LoanType] = None
    loan_amount: Optional[float] = Field(None, gt=0, description="Requested Loan Amount")
    tenure_months: Optional[int] = Field(None, gt=0, le=360, description="Loan Tenure in Months")
    interest_rate: Optional[float] = Field(None, gt=0, le=50, description="Interest Rate per annum")


class EntityOnboardingComplete(EntityOnboardingStep1, EntityOnboardingStep2):
    """Complete Entity Onboarding"""
    pass


class EntityResponse(BaseModel):
    """Entity Response Schema"""
    id: int
    cin: str
    pan: str
    name: str
    sector: str
    turnover: float
    loan_type: Optional[LoanType] = None
    loan_amount: Optional[float] = None
    tenure_months: Optional[int] = None
    interest_rate: Optional[float] = None
    status: EntityStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EntityValidationRequest(BaseModel):
    """Request to validate CIN/PAN"""
    cin: Optional[str] = None
    pan: Optional[str] = None


class EntityValidationResponse(BaseModel):
    """Response for CIN/PAN validation"""
    valid: bool
    message: str
    entity_id: Optional[int] = None
