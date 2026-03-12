from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AnnualReport(Base):
    """Annual Report financial data extracted from documents"""
    __tablename__ = "annual_reports"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    
    # Financial Year
    year = Column(Integer, nullable=False)
    
    # Key Financial Metrics
    revenue = Column(Float, nullable=True)
    ebitda = Column(Float, nullable=True)
    net_profit = Column(Float, nullable=True)
    cashflow_from_operations = Column(Float, nullable=True)
    total_debt = Column(Float, nullable=True)
    total_equity = Column(Float, nullable=True)
    
    # Calculated Ratios
    debt_to_equity = Column(Float, nullable=True)
    interest_coverage = Column(Float, nullable=True)  # EBITDA / Interest
    profit_margin = Column(Float, nullable=True)
    
    # Source
    source_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    extraction_confidence = Column(Float, nullable=True)
    is_manual_override = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    entity = relationship("Entity", back_populates="annual_reports")

    def __repr__(self):
        return f"<AnnualReport(id={self.id}, entity_id={self.entity_id}, year={self.year})>"
