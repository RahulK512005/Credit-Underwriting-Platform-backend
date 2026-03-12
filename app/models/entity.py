from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class EntityStatus(str, enum.Enum):
    ONBOARDED = "onboarded"
    DOCUMENTS_UPLOADED = "documents_uploaded"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class LoanType(str, enum.Enum):
    TERM_LOAN = "term_loan"
    WORKING_CAPITAL = "working_capital"
    OVERDRAFT = "overdraft"
    CAR_LOAN = "car_loan"
    BUSINESS_LOAN = "business_loan"


class Entity(Base):
    """Entity/Company model for credit underwriting"""
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    
    # Entity Details (Step 1)
    cin = Column(String(21), unique=True, index=True, nullable=False)
    pan = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=False)
    turnover = Column(Float, nullable=False)
    
    # Loan Details (Step 2)
    loan_type = Column(Enum(LoanType), nullable=True)
    loan_amount = Column(Float, nullable=True)
    tenure_months = Column(Integer, nullable=True)
    interest_rate = Column(Float, nullable=True)
    
    # Status
    status = Column(Enum(EntityStatus), default=EntityStatus.ONBOARDED)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    annual_reports = relationship("AnnualReport", back_populates="entity", cascade="all, delete-orphan")
    borrowing_profiles = relationship("BorrowingProfile", back_populates="entity", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="entity", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Entity(id={self.id}, name={self.name}, CIN={self.cin})>"


class Document(Base):
    """Document model for storing uploaded files"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, xlsx, etc.
    document_class = Column(String(50), nullable=True)  # annual_report, borrowing_profile
    classification_confidence = Column(Float, nullable=True)
    
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    entity = relationship("Entity", back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, type={self.document_class})>"
