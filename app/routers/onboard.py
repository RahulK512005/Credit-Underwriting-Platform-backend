from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Entity, EntityStatus
from app.schemas import (
    EntityOnboardingStep1,
    EntityOnboardingStep2,
    EntityOnboardingComplete,
    EntityResponse,
    EntityValidationRequest,
    EntityValidationResponse
)

router = APIRouter(prefix="/onboard", tags=["Onboarding"])


@router.post("", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def onboard_entity(
    data: EntityOnboardingComplete,
    db: Session = Depends(get_db)
):
    """
    Complete entity onboarding with both entity details and loan details
    """
    # Check if CIN already exists
    existing_cin = db.query(Entity).filter(Entity.cin == data.cin).first()
    if existing_cin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Entity with CIN {data.cin} already exists"
        )
    
    # Check if PAN already exists
    existing_pan = db.query(Entity).filter(Entity.pan == data.pan).first()
    if existing_pan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Entity with PAN {data.pan} already exists"
        )
    
    # Create new entity
    entity = Entity(
        cin=data.cin.upper(),
        pan=data.pan.upper(),
        name=data.name,
        sector=data.sector,
        turnover=data.turnover,
        loan_type=data.loan_type,
        loan_amount=data.loan_amount,
        tenure_months=data.tenure_months,
        interest_rate=data.interest_rate,
        status=EntityStatus.ONBOARDED
    )
    
    db.add(entity)
    db.commit()
    db.refresh(entity)
    
    return entity


@router.post("/validate", response_model=EntityValidationResponse)
def validate_entity(
    request: EntityValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Validate CIN or PAN (stub implementation)
    """
    if not request.cin and not request.pan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either CIN or PAN must be provided"
        )
    
    # Stub validation - in production, this would call external APIs
    if request.cin:
        entity = db.query(Entity).filter(Entity.cin == request.cin.upper()).first()
        if entity:
            return EntityValidationResponse(
                valid=False,
                message=f"CIN {request.cin} is already registered",
                entity_id=entity.id
            )
        # Validate CIN format
        if len(request.cin) != 21 or not request.cin.isalnum():
            return EntityValidationResponse(
                valid=False,
                message="Invalid CIN format"
            )
        return EntityValidationResponse(
            valid=True,
            message="CIN is valid and available"
        )
    
    if request.pan:
        entity = db.query(Entity).filter(Entity.pan == request.pan.upper()).first()
        if entity:
            return EntityValidationResponse(
                valid=False,
                message=f"PAN {request.pan} is already registered",
                entity_id=entity.id
            )
        # Validate PAN format
        if len(request.pan) != 10 or not request.pan[:5].isalpha() or not request.pan[5:9].isdigit() or not request.pan[9].isalpha():
            return EntityValidationResponse(
                valid=False,
                message="Invalid PAN format"
            )
        return EntityValidationResponse(
            valid=True,
            message="PAN is valid and available"
        )


@router.get("/{entity_id}", response_model=EntityResponse)
def get_entity(
    entity_id: int,
    db: Session = Depends(get_db)
):
    """
    Get entity details by ID
    """
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {entity_id} not found"
        )
    return entity


@router.put("/{entity_id}", response_model=EntityResponse)
def update_entity(
    entity_id: int,
    data: EntityOnboardingStep2,
    db: Session = Depends(get_db)
):
    """
    Update entity loan details
    """
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {entity_id} not found"
        )
    
    # Update loan details
    if data.loan_type is not None:
        entity.loan_type = data.loan_type
    if data.loan_amount is not None:
        entity.loan_amount = data.loan_amount
    if data.tenure_months is not None:
        entity.tenure_months = data.tenure_months
    if data.interest_rate is not None:
        entity.interest_rate = data.interest_rate
    
    db.commit()
    db.refresh(entity)
    
    return entity


@router.get("", response_model=list[EntityResponse])
def list_entities(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all entities with pagination
    """
    entities = db.query(Entity).offset(skip).limit(limit).all()
    return entities
