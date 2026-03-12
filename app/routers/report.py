from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Entity, AnnualReport, BorrowingProfile
from app.services import pdf_generator, recommendation_engine

router = APIRouter(prefix="/report", tags=["Report"])


@router.get("/{entity_id}")
def get_report_data(
    entity_id: int,
    db: Session = Depends(get_db)
):
    """
    Get report data for preview (without generating PDF)
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
    
    # Entity data
    entity_data = {
        'id': entity.id,
        'name': entity.name,
        'cin': entity.cin,
        'pan': entity.pan,
        'sector': entity.sector,
        'turnover': entity.turnover,
        'loan_type': entity.loan_type.value if entity.loan_type else None,
        'loan_amount': entity.loan_amount,
        'tenure_months': entity.tenure_months,
        'interest_rate': entity.interest_rate,
        'status': entity.status.value,
    }
    
    # Annual report data
    annual_report_data = {}
    if annual_reports:
        ar = annual_reports[0]
        annual_report_data = {
            'year': ar.year,
            'revenue': ar.revenue,
            'ebitda': ar.ebitda,
            'net_profit': ar.net_profit,
            'cashflow_from_operations': ar.cashflow_from_operations,
            'total_debt': ar.total_debt,
            'total_equity': ar.total_equity,
            'debt_to_equity': ar.debt_to_equity,
            'interest_coverage': ar.interest_coverage,
            'profit_margin': ar.profit_margin,
        }
    
    # Borrowing profile data
    borrowing_profile_data = {}
    if borrowing_profiles:
        bp = borrowing_profiles[0]
        borrowing_profile_data = {
            'loan_amount': bp.loan_amount,
            'tenure_months': bp.tenure_months,
            'interest_rate': bp.interest_rate,
            'emi': bp.emi,
            'purpose': bp.purpose,
            'lender_name': bp.lender_name,
            'repayment_schedule': bp.repayment_schedule,
        }
    
    # Get recommendation
    recommendation_data = {}
    if annual_report_data:
        result = recommendation_engine.analyze(
            entity_data=entity_data,
            annual_report_data=annual_report_data,
            borrowing_profile_data=borrowing_profile_data
        )
        recommendation_data = {
            'status': result.status.value,
            'score': result.score,
            'reasoning': result.reasoning,
            'warnings': result.warnings,
            'swot_analysis': result.swot_analysis,
        }
    
    return {
        "entity": entity_data,
        "annual_report": annual_report_data,
        "borrowing_profile": borrowing_profile_data,
        "recommendation": recommendation_data,
        "historical_data": [
            {
                'year': ar.year,
                'revenue': ar.revenue,
                'ebitda': ar.ebitda,
                'net_profit': ar.net_profit,
                'debt_to_equity': ar.debt_to_equity,
            }
            for ar in annual_reports
        ]
    }


@router.get("/{entity_id}/pdf")
def generate_pdf_report(
    entity_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate and download PDF report
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
        'status': entity.status.value,
    }
    
    # Annual report data
    annual_report_data = {
        'year': None,
        'revenue': 0,
        'ebitda': 0,
        'net_profit': 0,
        'cashflow_from_operations': 0,
        'total_debt': 0,
        'total_equity': 0,
        'debt_to_equity': 0,
        'interest_coverage': 0,
        'profit_margin': 0,
    }
    if annual_reports:
        ar = annual_reports[0]
        annual_report_data = {
            'year': ar.year,
            'revenue': ar.revenue or 0,
            'ebitda': ar.ebitda or 0,
            'net_profit': ar.net_profit or 0,
            'cashflow_from_operations': ar.cashflow_from_operations or 0,
            'total_debt': ar.total_debt or 0,
            'total_equity': ar.total_equity or 0,
            'debt_to_equity': ar.debt_to_equity or 0,
            'interest_coverage': ar.interest_coverage or 0,
            'profit_margin': ar.profit_margin or 0,
        }
    
    # Borrowing profile data
    borrowing_profile_data = {}
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
    
    # Get recommendation
    recommendation_data = {}
    if annual_report_data.get('year'):
        result = recommendation_engine.analyze(
            entity_data=entity_data,
            annual_report_data=annual_report_data,
            borrowing_profile_data=borrowing_profile_data
        )
        recommendation_data = {
            'status': result.status.value,
            'score': result.score,
            'reasoning': result.reasoning,
            'warnings': result.warnings,
            'swot_analysis': result.swot_analysis,
        }
    
    # Generate PDF
    pdf_bytes = pdf_generator.generate_report(
        entity_data=entity_data,
        annual_report_data=annual_report_data,
        borrowing_profile_data=borrowing_profile_data,
        recommendation_data=recommendation_data
    )
    
    # Return PDF
    filename = f"credit_report_{entity.cin}_{entity_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
