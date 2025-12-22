"""
Analysis Service
Business logic for tax residency analysis
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.db.models import Analysis, AnalysisStatus, ResidencyStatus
from app.schemas.residency import AnalysisCreate, AnalysisResponse
from app.graph.residency_workflow import get_residency_workflow

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for managing tax residency analyses"""

    @staticmethod
    async def create_analysis(
        db: Session,
        user_id: UUID,
        analysis_data: AnalysisCreate
    ) -> Analysis:
        """
        Create a new analysis

        Args:
            db: Database session
            user_id: ID of the user creating the analysis
            analysis_data: Analysis creation data

        Returns:
            Created Analysis model
        """
        # Create analysis record
        analysis = Analysis(
            user_id=user_id,
            title=analysis_data.title or f"{analysis_data.origin_country} → {analysis_data.destination_country}",
            origin_country=analysis_data.origin_country,
            destination_country=analysis_data.destination_country,
            departure_date=analysis_data.departure_date,
            user_profile=analysis_data.user_profile.dict(),
            status=AnalysisStatus.PENDING,
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        logger.info(f"Created analysis {analysis.id} for user {user_id}")
        return analysis

    @staticmethod
    async def run_analysis(
        db: Session,
        analysis_id: UUID
    ) -> Analysis:
        """
        Execute the analysis workflow

        Args:
            db: Database session
            analysis_id: ID of the analysis to run

        Returns:
            Updated Analysis model with results
        """
        # Get analysis
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise ValueError(f"Analysis {analysis_id} not found")

        # Update status to processing
        analysis.status = AnalysisStatus.PROCESSING
        db.commit()

        logger.info(f"Running analysis {analysis_id}")

        try:
            # Get workflow
            workflow = get_residency_workflow()

            # Run analysis
            start_time = datetime.utcnow()
            result = await workflow.run(
                user_profile=analysis.user_profile,
                origin_country=analysis.origin_country,
                destination_country=analysis.destination_country
            )
            end_time = datetime.utcnow()

            # Calculate processing time
            processing_time = (end_time - start_time).total_seconds()

            # Map status strings to enum
            origin_status_map = {
                "resident": ResidencyStatus.RESIDENT,
                "non-resident": ResidencyStatus.NON_RESIDENT,
                "deemed-resident": ResidencyStatus.DEEMED_RESIDENT,
                "factual-resident": ResidencyStatus.FACTUAL_RESIDENT,
            }
            dest_status_map = {
                "resident": ResidencyStatus.RESIDENT,
                "non-resident": ResidencyStatus.NON_RESIDENT,
            }

            # Update analysis with results
            analysis.status = AnalysisStatus.COMPLETED
            analysis.origin_residency_status = origin_status_map.get(
                result.get("origin_residency_status"),
                ResidencyStatus.RESIDENT
            )
            analysis.destination_residency_status = dest_status_map.get(
                result.get("destination_residency_status"),
                ResidencyStatus.RESIDENT
            )
            analysis.confidence_score = result.get("confidence_score")
            analysis.key_factors = result.get("key_factors", [])
            analysis.recommendations = result.get("recommendations", [])
            analysis.red_flags = result.get("red_flags", [])
            analysis.reasoning = f"Origin: {result.get('origin_reasoning', '')}\n\nDestination: {result.get('destination_reasoning', '')}"
            analysis.processing_time_seconds = processing_time
            analysis.completed_at = end_time

            db.commit()
            db.refresh(analysis)

            logger.info(f"Analysis {analysis_id} completed successfully in {processing_time:.2f}s")
            return analysis

        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed: {str(e)}")

            # Update status to failed
            analysis.status = AnalysisStatus.FAILED
            analysis.reasoning = f"Error: {str(e)}"
            db.commit()

            raise

    @staticmethod
    def get_analysis(
        db: Session,
        analysis_id: UUID,
        user_id: Optional[UUID] = None
    ) -> Optional[Analysis]:
        """
        Get an analysis by ID

        Args:
            db: Database session
            analysis_id: ID of the analysis
            user_id: Optional user ID for authorization check

        Returns:
            Analysis model or None
        """
        query = db.query(Analysis).filter(Analysis.id == analysis_id)

        if user_id:
            query = query.filter(Analysis.user_id == user_id)

        return query.first()

    @staticmethod
    def list_user_analyses(
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[Analysis]:
        """
        List all analyses for a user

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Analysis models
        """
        return (
            db.query(Analysis)
            .filter(Analysis.user_id == user_id)
            .order_by(Analysis.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def delete_analysis(
        db: Session,
        analysis_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete an analysis

        Args:
            db: Database session
            analysis_id: ID of the analysis
            user_id: User ID for authorization

        Returns:
            True if deleted, False if not found
        """
        analysis = (
            db.query(Analysis)
            .filter(Analysis.id == analysis_id, Analysis.user_id == user_id)
            .first()
        )

        if not analysis:
            return False

        db.delete(analysis)
        db.commit()

        logger.info(f"Deleted analysis {analysis_id}")
        return True
