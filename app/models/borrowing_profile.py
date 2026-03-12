from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class BorrowingProfile(Base):
    """Borrowing Profile data extracted from loan documents"""
    __tablename__ = "borrowing_profiles"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    
    # Loan Details
    loan_amount = Column(Float, nullable=True)
    tenure_months = Column(Integer, nullable=True)
    interest_rate = Column(Float, nullable=True)
    emi = Column(Float, nullable=True)
    
    # Repayment Schedule (stored as JSON)
    repayment_schedule = Column(JSON, nullable=True)
    
    # Loan Purpose
    purpose = Column(String(255), nullable=True)
    lender_name = Column(String(255), nullable=True)
    
    # Source
    source_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    extraction_confidence = Column(Float, nullable=True)
    is_manual_override = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    entity = relationship("Entity", back_populates="borrowing_profiles")

    def __repr__(self):
        return f"<BorrowingProfile(id={self.id}, entity_id={self.entity_id}, amount={self.loan_amount})>"
