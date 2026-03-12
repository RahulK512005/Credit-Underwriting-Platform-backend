from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import Entity, AnnualReport, BorrowingProfile, EntityStatus
from app.services import recommendation_engine

router = APIRouter(prefix="/recommend", tags=["Recommendation"])


class RecommendRequest(BaseModel):
    """Request body for recommendation"""
    entity_id: int
    force_recalculate: bool = False


class RecommendationResponse(BaseModel):
    """Response for recommendation"""
    entity_id: int
    status: str
    score: float
    reasoning: str
    warnings: list
    swot_analysis: dict


@router.post("", response_model=RecommendationResponse)
def get_recommendation(
    request: RecommendRequest,
    db: Session = Depends(get_db)
):
    """
    Get credit recommendation for an entity
    """
    # Get entity
    entity = db.query(Entity).filter(Entity.id == request.entity_id).first()
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {request.entity_id} not found"
        )
    
    # Get annual reports
    annual_reports = db.query(AnnualReport).filter(
        AnnualReport.entity_id == request.entity_id
    ).order_by(AnnualReport.year.desc()).all()
    
    # Get borrowing profiles
    borrowing_profiles = db.query(BorrowingProfile).filter(
        BorrowingProfile.entity_id == request.entity_id
    ).all()
    
    if not annual_reports:
        # Return default recommendation if no financial data
        default = recommendation_engine.get_default_recommendation()
        return RecommendationResponse(
            entity_id=request.entity_id,
            status=default.status.value,
            score=default.score,
            reasoning=default.reasoning,
            warnings=default.warnings,
            swot_analysis=default.swot_analysis
        )
    
    # Use the most recent annual report
    latest_report = annual_reports[0]
    
    # Convert to dict for analysis
    annual_report_data = {
        'year': latest_report.year,
        'revenue': latest_report.revenue,
        'ebitda': latest_report.ebitda,
        'net_profit': latest_report.net_profit,
        'cashflow_from_operations': latest_report.cashflow_from_operations,
        'total_debt': latest_report.total_debt,
        'total_equity': latest_report.total_equity,
        'debt_to_equity': latest_report.debt_to_equity,
        'interest_coverage': latest_report.interest_coverage,
        'profit_margin': latest_report.profit_margin,
    }
    
    # Entity data
    entity_data = {
        'name': entity.name,
        'cin': entity.cin,
        'pan': entity.pan,
        'sector': entity.sector,
        'turnover': entity.turnover,
        'loan_type': entity.loan_type.value if entity.loan_type else None,
        'loan_amount': entity.loan_amount,
        'tenure_months': entity.tenure_months,
        'interest_rate': entity.interest_rate,
    }
    
    # Borrowing profile data
    borrowing_profile_data = None
    if borrowing_profiles:
        bp = borrowing_profiles[0]
        borrowing_profile_data = {
            'loan_amount': bp.loan_amount,
            'tenure_months': bp.tenure_months,
            'interest_rate': bp.interest_rate,
            'emi': bp.emi,
            'purpose': bp.purpose,
            'lender_name': bp.lender_name,
        }
    
    # Generate recommendation
    result = recommendation_engine.analyze(
        entity_data=entity_data,
        annual_report_data=annual_report_data,
        borrowing_profile_data=borrowing_profile_data
    )
    
    # Update entity status based on recommendation
    if request.force_recalculate or entity.status == EntityStatus.DOCUMENTS_UPLOADED:
        if result.status.value == "approved":
            entity.status = EntityStatus.APPROVED
        elif result.status.value == "rejected":
            entity.status = EntityStatus.REJECTED
        else:
            entity.status = EntityStatus.UNDER_REVIEW
        db.commit()
    
    return RecommendationResponse(
        entity_id=request.entity_id,
        status=result.status.value,
        score=result.score,
        reasoning=result.reasoning,
        warnings=result.warnings,
        swot_analysis=result.swot_analysis
    )


@router.get("/{entity_id}")
def get_recommendation_by_entity(
    entity_id: int,
    db: Session = Depends(get_db)
):
    """
    Get recommendation for an entity (GET method)
    """
    # Get entity
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {entity_id} not found"
        )
    
    # Get annual reports
    annual_reports = db.query(AnnualReport).filter(
        AnnualReport.entity_id == entity_id
    ).order_by(AnnualReport.year.desc()).all()
    
    # Get borrowing profiles
    borrowing_profiles = db.query(BorrowingProfile).filter(
        BorrowingProfile.entity_id == entity_id
    ).all()
    
    if not annual_reports:
        default = recommendation_engine.get_default_recommendation()
        return {
            "entity_id": entity_id,
            "status": default.status.value,
            "score": default.score,
            "reasoning": default.reasoning,
            "warnings": default.warnings,
            "swot_analysis": default.swot_analysis
        }
    
    latest_report = annual_reports[0]
    
    annual_report_data = {
        'year': latest_report.year,
        'revenue': latest_report.revenue,
        'ebitda': latest_report.ebitda,
        'net_profit': latest_report.net_profit,
        'cashflow_from_operations': latest_report.cashflow_from_operations,
        'total_debt': latest_report.total_debt,
        'total_equity': latest_report.total_equity,
        'debt_to_equity': latest_report.debt_to_equity,
        'interest_coverage': latest_report.interest_coverage,
        'profit_margin': latest_report.profit_margin,
    }
    
    entity_data = {
        'name': entity.name,
        'cin': entity.cin,
        'pan': entity.pan,
        'sector': entity.sector,
        'turnover': entity.turnover,
        'loan_type': entity.loan_type.value if entity.loan_type else None,
        'loan_amount': entity.loan_amount,
        'tenure_months': entity.tenure_months,
        'interest_rate': entity.interest_rate,
    }
    
    borrowing_profile_data = None
    if borrowing_profiles:
        bp = borrowing_profiles[0]
        borrowing_profile_data = {
            'loan_amount': bp.loan_amount,
            'tenure_months': bp.tenure_months,
            'interest_rate': bp.interest_rate,
            'emi': bp.emi,
        }
    
    result = recommendation_engine.analyze(
        entity_data=entity_data,
        annual_report_data=annual_report_data,
        borrowing_profile_data=borrowing_profile_data
    )
    
    return {
        "entity_id": entity_id,
        "status": result.status.value,
        "score": result.score,
        "reasoning": result.reasoning,
        "warnings": result.warnings,
        "swot_analysis": result.swot_analysis
    }
