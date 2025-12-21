"""
Base Agent Class
Provides common functionality for all agents in TaxCompass
"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import time
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all TaxCompass agents"""

    def __init__(self, name: str):
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main logic

        Args:
            input_data: Input data for the agent

        Returns:
            Dict containing the agent's output
        """
        pass

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wrapper around execute that adds timing and error handling

        Args:
            input_data: Input data for the agent

        Returns:
            Dict containing the agent's output and metadata
        """
        self.start_time = time.time()
        logger.info(f"Agent '{self.name}' starting execution")

        try:
            result = await self.execute(input_data)
            self.end_time = time.time()

            execution_time = self.end_time - self.start_time
            logger.info(f"Agent '{self.name}' completed in {execution_time:.2f}s")

            return {
                **result,
                "metadata": {
                    "agent_name": self.name,
                    "execution_time": execution_time,
                    "status": "success"
                }
            }
        except Exception as e:
            self.end_time = time.time()
            execution_time = self.end_time - self.start_time

            logger.error(f"Agent '{self.name}' failed after {execution_time:.2f}s: {str(e)}")

            return {
                "error": str(e),
                "metadata": {
                    "agent_name": self.name,
                    "execution_time": execution_time,
                    "status": "failed"
                }
            }

    def get_execution_time(self) -> Optional[float]:
        """Get the execution time in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
