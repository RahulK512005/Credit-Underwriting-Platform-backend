from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Entity, Document, AnnualReport, BorrowingProfile, EntityStatus
from app.schemas import AnnualReportResponse, BorrowingProfileResponse, AnnualReportUpdate, BorrowingProfileUpdate

router = APIRouter(prefix="/extract", tags=["Extraction"])


@router.get("/{entity_id}")
def get_extracted_data(
    entity_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all extracted data for an entity
    """
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {entity_id} not found"
        )
    
    # Get annual reports
    annual_reports = db.query(AnnualReport).filter(
        AnnualReport.entity_id == entity_id
    ).all()
    
    # Get borrowing profiles
    borrowing_profiles = db.query(BorrowingProfile).filter(
        BorrowingProfile.entity_id == entity_id
    ).all()
    
    return {
        "entity_id": entity_id,
        "entity_name": entity.name,
        "annual_reports": [
            {
                "id": ar.id,
                "year": ar.year,
                "revenue": ar.revenue,
                "ebitda": ar.ebitda,
                "net_profit": ar.net_profit,
                "cashflow_from_operations": ar.cashflow_from_operations,
                "total_debt": ar.total_debt,
                "total_equity": ar.total_equity,
                "debt_to_equity": ar.debt_to_equity,
                "interest_coverage": ar.interest_coverage,
                "profit_margin": ar.profit_margin,
                "extraction_confidence": ar.extraction_confidence,
                "is_manual_override": ar.is_manual_override,
                "created_at": ar.created_at.isoformat() if ar.created_at else None
            }
            for ar in annual_reports
        ],
        "borrowing_profiles": [
            {
                "id": bp.id,
                "loan_amount": bp.loan_amount,
                "tenure_months": bp.tenure_months,
                "interest_rate": bp.interest_rate,
                "emi": bp.emi,
                "purpose": bp.purpose,
                "lender_name": bp.lender_name,
                "extraction_confidence": bp.extraction_confidence,
                "is_manual_override": bp.is_manual_override,
                "created_at": bp.created_at.isoformat() if bp.created_at else None
            }
            for bp in borrowing_profiles
        ]
    }


@router.post("/{entity_id}/annual-report")
def create_annual_report(
    entity_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """
    Create or update annual report data
    """
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {entity_id} not found"
        )
    
    # Check if annual report for this year exists
    year = data.get('year')
    existing_report = db.query(AnnualReport).filter(
        AnnualReport.entity_id == entity_id,
        AnnualReport.year == year
    ).first()
    
    if existing_report:
        # Update existing
        for key, value in data.items():
            if hasattr(existing_report, key):
                setattr(existing_report, key, value)
        existing_report.is_manual_override = True
        db.refresh(existing_report)
        return {"message": "Annual report updated", "id": existing_report.id}
    
    # Create new
    annual_report = AnnualReport(
        entity_id=entity_id,
        year=data.get('year'),
        revenue=data.get('revenue'),
        ebitda=data.get('ebitda'),
        net_profit=data.get('net_profit'),
        cashflow_from_operations=data.get('cashflow_from_operations'),
        total_debt=data.get('total_debt'),
        total_equity=data.get('total_equity'),
        debt_to_equity=data.get('debt_to_equity'),
        interest_coverage=data.get('interest_coverage'),
        profit_margin=data.get('profit_margin'),
        extraction_confidence=data.get('extraction_confidence', 1.0),
        is_manual_override=True
    )
    
    db.add(annual_report)
    db.commit()
    db.refresh(annual_report)
    
    return {"message": "Annual report created", "id": annual_report.id}


@router.put("/annual-report/{report_id}")
def update_annual_report(
    report_id: int,
    data: AnnualReportUpdate,
    db: Session = Depends(get_db)
):
    """
    Update annual report data
    """
    report = db.query(AnnualReport).filter(AnnualReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Annual report with ID {report_id} not found"
        )
    
    # Update fields
    for key, value in data.model_dump(exclude_unset=True).items():
        if hasattr(report, key):
            setattr(report, key, value)
    
    if data.is_manual_override is not None:
        report.is_manual_override = data.is_manual_override
    
    db.commit()
    db.refresh(report)
    
    return {"message": "Annual report updated", "id": report.id}


@router.post("/{entity_id}/borrowing-profile")
def create_borrowing_profile(
    entity_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """
    Create or update borrowing profile data
    """
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {entity_id} not found"
        )
    
    # Check if borrowing profile exists
    existing_profile = db.query(BorrowingProfile).filter(
        BorrowingProfile.entity_id == entity_id
    ).first()
    
    if existing_profile:
        # Update existing
        for key, value in data.items():
            if hasattr(existing_profile, key):
                setattr(existing_profile, key, value)
        existing_profile.is_manual_override = True
        db.refresh(existing_profile)
        return {"message": "Borrowing profile updated", "id": existing_profile.id}
    
    # Create new
    borrowing_profile = BorrowingProfile(
        entity_id=entity_id,
        loan_amount=data.get('loan_amount'),
        tenure_months=data.get('tenure_months'),
        interest_rate=data.get('interest_rate'),
        emi=data.get('emi'),
        purpose=data.get('purpose'),
        lender_name=data.get('lender_name'),
        repayment_schedule=data.get('repayment_schedule'),
        extraction_confidence=data.get('extraction_confidence', 1.0),
        is_manual_override=True
    )
    
    db.add(borrowing_profile)
    db.commit()
    db.refresh(borrowing_profile)
    
    return {"message": "Borrowing profile created", "id": borrowing_profile.id}


@router.put("/borrowing-profile/{profile_id}")
def update_borrowing_profile(
    profile_id: int,
    data: BorrowingProfileUpdate,
    db: Session = Depends(get_db)
):
    """
    Update borrowing profile data
    """
    profile = db.query(BorrowingProfile).filter(BorrowingProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Borrowing profile with ID {profile_id} not found"
        )
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    if 'repayment_schedule' in update_data:
        # Convert to list if it's a list of dicts
        schedule = update_data['repayment_schedule']
        if schedule:
            update_data['repayment_schedule'] = [
                item.dict() if hasattr(item, 'dict') else item 
                for item in schedule
            ]
    
    for key, value in update_data.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
    
    if data.is_manual_override is not None:
        profile.is_manual_override = data.is_manual_override
    
    db.commit()
    db.refresh(profile)
    
    return {"message": "Borrowing profile updated", "id": profile.id}


@router.delete("/annual-report/{report_id}")
def delete_annual_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete annual report
    """
    report = db.query(AnnualReport).filter(AnnualReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Annual report with ID {report_id} not found"
        )
    
    db.delete(report)
    db.commit()
    
    return {"message": "Annual report deleted"}


@router.delete("/borrowing-profile/{profile_id}")
def delete_borrowing_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete borrowing profile
    """
    profile = db.query(BorrowingProfile).filter(BorrowingProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Borrowing profile with ID {profile_id} not found"
        )
    
    db.delete(profile)
    db.commit()
    
    return {"message": "Borrowing profile deleted"}
