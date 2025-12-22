"""
Analysis API Endpoints
Handles tax residency analysis requests
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User
from app.schemas.residency import (
    AnalysisCreate,
    AnalysisResponse,
    AnalysisRunRequest
)
from app.services.analysis_service import AnalysisService
from app.utils.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    analysis_data: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new tax residency analysis

    Creates a new analysis record and optionally runs it immediately.
    """
    analysis = await AnalysisService.create_analysis(
        db=db,
        user_id=current_user.id,
        analysis_data=analysis_data
    )

    return analysis


@router.post("/{analysis_id}/run", response_model=AnalysisResponse)
async def run_analysis(
    analysis_id: UUID,
    background_tasks: BackgroundTasks,
    run_request: AnalysisRunRequest = AnalysisRunRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Execute an analysis

    Runs the residency analyzer agent workflow.
    Returns immediately with status='processing' and runs analysis in background.
    """
    # Verify analysis exists and belongs to user
    analysis = AnalysisService.get_analysis(
        db=db,
        analysis_id=analysis_id,
        user_id=current_user.id
    )

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # For MVP, run synchronously (in production would use background tasks)
    analysis = await AnalysisService.run_analysis(
        db=db,
        analysis_id=analysis_id
    )

    return analysis


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get an analysis by ID

    Returns the analysis details and results if completed.
    """
    analysis = AnalysisService.get_analysis(
        db=db,
        analysis_id=analysis_id,
        user_id=current_user.id
    )

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    return analysis


@router.get("/", response_model=List[AnalysisResponse])
async def list_analyses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all analyses for the current user

    Returns a paginated list of analyses ordered by creation date (newest first).
    """
    analyses = AnalysisService.list_user_analyses(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

    return analyses


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an analysis

    Permanently deletes an analysis and all associated data.
    """
    deleted = AnalysisService.delete_analysis(
        db=db,
        analysis_id=analysis_id,
        user_id=current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    return None


@router.post("/quick-analysis", response_model=AnalysisResponse)
async def quick_analysis(
    analysis_data: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create and run analysis in one step

    Convenience endpoint that creates an analysis and immediately runs it.
    Returns the completed analysis results.
    """
    # Create analysis
    analysis = await AnalysisService.create_analysis(
        db=db,
        user_id=current_user.id,
        analysis_data=analysis_data
    )

    # Run analysis
    analysis = await AnalysisService.run_analysis(
        db=db,
        analysis_id=analysis.id
    )

    return analysis
