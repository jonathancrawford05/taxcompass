"""
LangGraph Workflow for Residency Analysis
Orchestrates the multi-step residency determination process
"""
from typing import Dict, Any, TypedDict, Annotated
import logging
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

from app.agents.residency_analyzer import ResidencyAnalyzerAgent
from app.schemas.residency import UserProfile

logger = logging.getLogger(__name__)


class ResidencyWorkflowState(TypedDict):
    """State for residency analysis workflow"""

    # Input
    user_profile: Dict[str, Any]
    origin_country: str
    destination_country: str

    # Intermediate results
    origin_analysis: Dict[str, Any]
    destination_analysis: Dict[str, Any]
    recommendations: list

    # Output
    final_analysis: Dict[str, Any]
    confidence_score: float

    # Metadata
    current_step: str
    errors: list


class ResidencyWorkflow:
    """
    LangGraph workflow for tax residency analysis

    Steps:
    1. Validate input
    2. Analyze origin country residency
    3. Analyze destination country residency
    4. Generate recommendations
    5. Compile final analysis
    """

    def __init__(self):
        self.analyzer_agent = ResidencyAnalyzerAgent()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""

        # Create graph
        workflow = StateGraph(ResidencyWorkflowState)

        # Add nodes
        workflow.add_node("validate_input", self._validate_input)
        workflow.add_node("analyze_residency", self._analyze_residency)
        workflow.add_node("compile_results", self._compile_results)

        # Define edges
        workflow.set_entry_point("validate_input")
        workflow.add_edge("validate_input", "analyze_residency")
        workflow.add_edge("analyze_residency", "compile_results")
        workflow.add_edge("compile_results", END)

        # Compile graph
        return workflow.compile()

    async def run(
        self,
        user_profile: Dict[str, Any],
        origin_country: str,
        destination_country: str
    ) -> Dict[str, Any]:
        """
        Run the residency analysis workflow

        Args:
            user_profile: User's tax situation
            origin_country: Origin country ISO code
            destination_country: Destination country ISO code

        Returns:
            Complete analysis results
        """
        logger.info(
            f"Starting residency workflow: {origin_country} → {destination_country}"
        )

        # Initialize state
        initial_state = {
            "user_profile": user_profile,
            "origin_country": origin_country,
            "destination_country": destination_country,
            "origin_analysis": {},
            "destination_analysis": {},
            "recommendations": [],
            "final_analysis": {},
            "confidence_score": 0.0,
            "current_step": "init",
            "errors": []
        }

        # Run workflow
        try:
            final_state = await self.graph.ainvoke(initial_state)
            logger.info("Residency workflow completed successfully")
            return final_state["final_analysis"]

        except Exception as e:
            logger.error(f"Residency workflow failed: {str(e)}")
            raise

    async def _validate_input(self, state: ResidencyWorkflowState) -> Dict[str, Any]:
        """Validate input data"""
        logger.info("Step 1: Validating input")

        errors = []

        # Validate required fields
        if not state.get("user_profile"):
            errors.append("user_profile is required")

        if not state.get("origin_country"):
            errors.append("origin_country is required")

        if not state.get("destination_country"):
            errors.append("destination_country is required")

        if errors:
            logger.error(f"Validation failed: {errors}")
            return {"errors": errors, "current_step": "validation_failed"}

        logger.info("Input validation passed")
        return {"current_step": "validated"}

    async def _analyze_residency(self, state: ResidencyWorkflowState) -> Dict[str, Any]:
        """Analyze residency using the analyzer agent"""
        logger.info("Step 2: Analyzing residency")

        try:
            # Run analyzer agent
            result = await self.analyzer_agent.run({
                "user_profile": state["user_profile"],
                "origin_country": state["origin_country"],
                "destination_country": state["destination_country"]
            })

            return {
                "origin_analysis": result.get("origin_analysis", {}),
                "destination_analysis": result.get("destination_analysis", {}),
                "recommendations": result.get("recommendations", []),
                "current_step": "analyzed"
            }

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {
                "errors": state.get("errors", []) + [str(e)],
                "current_step": "analysis_failed"
            }

    async def _compile_results(self, state: ResidencyWorkflowState) -> Dict[str, Any]:
        """Compile final analysis results"""
        logger.info("Step 3: Compiling results")

        origin_analysis = state.get("origin_analysis", {})
        destination_analysis = state.get("destination_analysis", {})

        # Calculate overall confidence (average of both analyses)
        origin_confidence = origin_analysis.get("confidence", 0.5)
        destination_confidence = destination_analysis.get("confidence", 0.5)
        overall_confidence = (origin_confidence + destination_confidence) / 2

        # Compile final analysis
        final_analysis = {
            "origin_country": state["origin_country"],
            "destination_country": state["destination_country"],

            # Origin results
            "origin_residency_status": origin_analysis.get("status"),
            "origin_confidence": origin_confidence,
            "origin_key_factors": origin_analysis.get("key_factors", []),
            "origin_reasoning": origin_analysis.get("reasoning"),

            # Destination results
            "destination_residency_status": destination_analysis.get("status"),
            "destination_confidence": destination_confidence,
            "destination_key_factors": destination_analysis.get("key_factors", []),
            "destination_reasoning": destination_analysis.get("reasoning"),

            # Combined analysis
            "confidence_score": overall_confidence,
            "key_factors": (
                origin_analysis.get("key_factors", []) +
                destination_analysis.get("key_factors", [])
            ),
            "red_flags": (
                origin_analysis.get("red_flags", []) +
                destination_analysis.get("red_flags", [])
            ),
            "recommendations": state.get("recommendations", []),

            # Status
            "status": "completed",
            "errors": state.get("errors", [])
        }

        return {
            "final_analysis": final_analysis,
            "confidence_score": overall_confidence,
            "current_step": "completed"
        }


# Singleton instance
_workflow = None


def get_residency_workflow() -> ResidencyWorkflow:
    """Get or create residency workflow singleton"""
    global _workflow
    if _workflow is None:
        _workflow = ResidencyWorkflow()
    return _workflow
