from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AnnualReportBase(BaseModel):
    """Base Annual Report Schema"""
    year: int = Field(..., ge=2000, le=2100)
    revenue: Optional[float] = None
    ebitda: Optional[float] = None
    net_profit: Optional[float] = None
    cashflow_from_operations: Optional[float] = None
    total_debt: Optional[float] = None
    total_equity: Optional[float] = None
    debt_to_equity: Optional[float] = None
    interest_coverage: Optional[float] = None
    profit_margin: Optional[float] = None


class AnnualReportCreate(AnnualReportBase):
    """Schema for creating Annual Report"""
    entity_id: int
    source_document_id: Optional[int] = None
    extraction_confidence: Optional[float] = Field(None, ge=0, le=1)


class AnnualReportUpdate(BaseModel):
    """Schema for updating Annual Report"""
    year: Optional[int] = Field(None, ge=2000, le=2100)
    revenue: Optional[float] = None
    ebitda: Optional[float] = None
    net_profit: Optional[float] = None
    cashflow_from_operations: Optional[float] = None
    total_debt: Optional[float] = None
    total_equity: Optional[float] = None
    debt_to_equity: Optional[float] = None
    interest_coverage: Optional[float] = None
    profit_margin: Optional[float] = None
    is_manual_override: Optional[bool] = None


class AnnualReportResponse(AnnualReportBase):
    """Schema for Annual Report Response"""
    id: int
    entity_id: int
    source_document_id: Optional[int] = None
    extraction_confidence: Optional[float] = None
    is_manual_override: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ExtractionResult(BaseModel):
    """Result from document extraction"""
    success: bool
    document_type: str
    data: dict
    confidence: float
    message: str
