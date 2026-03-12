from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RepaymentScheduleItem(BaseModel):
    """Individual repayment schedule entry"""
    month: int
    principal: float
    interest: float
    emi: float
    balance: float


class BorrowingProfileBase(BaseModel):
    """Base Borrowing Profile Schema"""
    loan_amount: Optional[float] = None
    tenure_months: Optional[int] = None
    interest_rate: Optional[float] = None
    emi: Optional[float] = None
    purpose: Optional[str] = None
    lender_name: Optional[str] = None


class BorrowingProfileCreate(BorrowingProfileBase):
    """Schema for creating Borrowing Profile"""
    entity_id: int
    source_document_id: Optional[int] = None
    extraction_confidence: Optional[float] = Field(None, ge=0, le=1)
    repayment_schedule: Optional[List[RepaymentScheduleItem]] = None


class BorrowingProfileUpdate(BaseModel):
    """Schema for updating Borrowing Profile"""
    loan_amount: Optional[float] = None
    tenure_months: Optional[int] = None
    interest_rate: Optional[float] = None
    emi: Optional[float] = None
    purpose: Optional[str] = None
    lender_name: Optional[str] = None
    repayment_schedule: Optional[List[RepaymentScheduleItem]] = None
    is_manual_override: Optional[bool] = None


class BorrowingProfileResponse(BorrowingProfileBase):
    """Schema for Borrowing Profile Response"""
    id: int
    entity_id: int
    source_document_id: Optional[int] = None
    extraction_confidence: Optional[float] = None
    is_manual_override: bool
    repayment_schedule: Optional[List[dict]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
