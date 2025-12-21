"""
Residency Analyzer Agent
Determines tax residency status for origin and destination countries
"""
from typing import Dict, Any, List
import logging
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

from app.agents.base import BaseAgent
from app.rag.retrievers import TaxLawRetriever
from app.schemas.residency import UserProfile, ResidencyAnalysis
from app.config import settings

logger = logging.getLogger(__name__)


class ResidencyAnalyzerAgent(BaseAgent):
    """
    Analyzes tax residency status using RAG over tax law documents

    This agent determines whether a user is a tax resident or non-resident
    in both their origin and destination countries based on their profile
    and relevant tax laws.
    """

    def __init__(self):
        super().__init__(name="ResidencyAnalyzer")

        # Initialize LLM
        self.llm = Ollama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.1,  # Low temperature for consistent, factual responses
        )

        # Initialize retriever
        self.retriever = TaxLawRetriever(k=5)

        # Create prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["user_profile", "tax_law_context", "country", "analysis_type"],
            template="""You are an expert tax residency analyst. Analyze the following user profile to determine their tax residency status.

USER PROFILE:
{user_profile}

RELEVANT TAX LAW ({country}):
{tax_law_context}

TASK: Determine if the user is a tax {analysis_type} in {country}.

Consider the following factors:
1. Physical presence (days in country)
2. Residential ties (home, spouse, dependents)
3. Economic ties (employment, property, bank accounts)
4. Citizenship and immigration status

Provide your analysis in the following JSON format:
{{
    "status": "resident" or "non-resident" or "deemed-resident" or "factual-resident",
    "confidence": 0.0 to 1.0,
    "key_factors": ["factor 1", "factor 2", ...],
    "reasoning": "detailed explanation of determination",
    "red_flags": ["warning 1", "warning 2", ...]
}}

Be specific and cite relevant tax rules where applicable.

ANALYSIS:"""
        )

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute residency analysis

        Args:
            input_data: Must contain:
                - user_profile: UserProfile dict
                - origin_country: ISO country code
                - destination_country: ISO country code

        Returns:
            Dict with origin_analysis and destination_analysis
        """
        try:
            # Extract input
            user_profile = input_data["user_profile"]
            origin_country = input_data["origin_country"]
            destination_country = input_data["destination_country"]

            logger.info(
                f"Analyzing residency for {origin_country} → {destination_country}"
            )

            # Analyze origin country
            origin_analysis = await self._analyze_country(
                user_profile=user_profile,
                country=origin_country,
                analysis_type="resident (staying)" if origin_country == user_profile.get("current_country") else "resident"
            )

            # Analyze destination country
            destination_analysis = await self._analyze_country(
                user_profile=user_profile,
                country=destination_country,
                analysis_type="resident (upon arrival)"
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                origin_analysis,
                destination_analysis,
                user_profile
            )

            return {
                "origin_analysis": origin_analysis,
                "destination_analysis": destination_analysis,
                "recommendations": recommendations,
            }

        except Exception as e:
            logger.error(f"Residency analysis failed: {str(e)}")
            raise

    async def _analyze_country(
        self,
        user_profile: Dict[str, Any],
        country: str,
        analysis_type: str
    ) -> Dict[str, Any]:
        """
        Analyze residency for a specific country

        Args:
            user_profile: User's tax situation
            country: Country code to analyze
            analysis_type: Type of analysis (e.g., "resident", "non-resident")

        Returns:
            Analysis results dict
        """
        # Build retrieval query
        query = self._build_retrieval_query(user_profile, country)

        # Retrieve relevant tax law context
        logger.info(f"Retrieving tax law context for {country}")
        retrieved_docs = await self.retriever.retrieve(
            query=query,
            country=country,
            k=5
        )

        # Format context
        tax_law_context = self.retriever.format_context(retrieved_docs)

        # If no context found, use placeholder
        if not retrieved_docs:
            tax_law_context = (
                f"[Note: No specific {country} tax law documents found in database. "
                f"Analysis will be based on general tax residency principles.]"
            )

        # Format user profile for prompt
        profile_text = self._format_user_profile(user_profile)

        # Generate prompt
        prompt = self.prompt_template.format(
            user_profile=profile_text,
            tax_law_context=tax_law_context,
            country=country,
            analysis_type=analysis_type
        )

        # Call LLM
        logger.info(f"Calling LLM for {country} analysis")
        response = self.llm.invoke(prompt)

        # Parse response (simplified - in production would use structured output)
        analysis = self._parse_llm_response(response)

        return analysis

    def _build_retrieval_query(
        self,
        user_profile: Dict[str, Any],
        country: str
    ) -> str:
        """Build query for retrieving relevant tax law"""
        situation = []

        if user_profile.get("has_spouse"):
            situation.append("married with spouse")
        if user_profile.get("has_dependents"):
            situation.append("with dependents")
        if user_profile.get("owns_home_origin"):
            situation.append("owns property")

        situation_str = ", ".join(situation) if situation else "individual"

        return (
            f"Tax residency determination for {country}. "
            f"Person {situation_str}. "
            f"Residential ties and physical presence tests."
        )

    def _format_user_profile(self, user_profile: Dict[str, Any]) -> str:
        """Format user profile for LLM prompt"""
        lines = []

        lines.append(f"Current Country: {user_profile.get('current_country')}")
        lines.append(f"Destination Country: {user_profile.get('destination_country')}")
        lines.append(f"Departure Date: {user_profile.get('departure_date')}")
        lines.append(f"Marital Status: {user_profile.get('marital_status')}")

        if user_profile.get('has_spouse'):
            lines.append(f"Spouse Location: {user_profile.get('spouse_location', 'Not specified')}")

        if user_profile.get('has_dependents'):
            lines.append(f"Dependents Location: {user_profile.get('dependents_location', 'Not specified')}")

        lines.append(f"Owns Home in Origin: {user_profile.get('owns_home_origin')}")
        if user_profile.get('home_disposition'):
            lines.append(f"Home Disposition: {user_profile.get('home_disposition')}")

        lines.append(f"Employment Type: {user_profile.get('employment_type')}")
        lines.append(f"Employer Country: {user_profile.get('employer_country')}")
        lines.append(f"Annual Income: ${user_profile.get('annual_income')}")

        return "\n".join(lines)

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured format

        In production, would use structured output or JSON mode
        For now, returns a simplified structure
        """
        import json
        import re

        # Try to extract JSON from response
        try:
            # Look for JSON block in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return parsed
        except:
            pass

        # Fallback: return basic structure
        return {
            "status": "resident",  # Default
            "confidence": 0.5,
            "key_factors": ["Analysis pending - structured output"],
            "reasoning": response,
            "red_flags": []
        }

    def _generate_recommendations(
        self,
        origin_analysis: Dict[str, Any],
        destination_analysis: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Check for dual residency
        if (origin_analysis.get("status") in ["resident", "deemed-resident"] and
            destination_analysis.get("status") in ["resident", "deemed-resident"]):
            recommendations.append(
                "⚠️ Potential dual tax residency detected. Review tax treaty provisions."
            )

        # Family separation issues
        if user_profile.get("has_spouse") and user_profile.get("spouse_location") != user_profile.get("destination_country"):
            recommendations.append(
                "Consider impact of family separation on residency determination."
            )

        # Property disposition
        if user_profile.get("owns_home_origin") and not user_profile.get("home_disposition"):
            recommendations.append(
                "Determine what to do with origin country property (sell, rent, or keep vacant)."
            )

        # Always recommend professional consultation
        recommendations.append(
            "Consult with a qualified tax professional to confirm residency status and obligations."
        )

        return recommendations
