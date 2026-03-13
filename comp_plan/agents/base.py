# comp_plan/agents/base.py - Agent base classes and enums
import logging
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AgentType(Enum):
    DOCUMENT_ANALYZER = "document_analyzer"
    RISK_ASSESSOR = "risk_assessor"
    ORACLE_MAPPER = "oracle_mapper"
    COMPLIANCE_CHECKER = "compliance_checker"
    OPTIMIZATION_ADVISOR = "optimization_advisor"
    DATA_EXTRACTOR = "data_extractor"
    REPORT_GENERATOR = "report_generator"


class AnalysisApproach(Enum):
    COMPREHENSIVE = "comprehensive"
    QUICK_SCAN = "quick_scan"
    RISK_FOCUSED = "risk_focused"
    TECHNICAL_MAPPING = "technical_mapping"
    CUSTOM = "custom"


@dataclass
class AgentResult:
    agent_name: str
    status: str  # success, failed, partial
    execution_time: float
    confidence_score: float
    data: Dict[str, Any]
    errors: List[str] = None
    warnings: List[str] = None


class BaseAgent:
    """Base class for all AI agents."""

    def __init__(self, name: str, description: str, model_preferences: List[str]):
        self.name = name
        self.description = description
        self.model_preferences = model_preferences
        self.execution_count = 0
        self.success_rate = 0.0

    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any] = None) -> AgentResult:
        """Execute the agent with given inputs."""
        start_time = datetime.now()
        try:
            result_data = await self._process(inputs, context or {})
            execution_time = (datetime.now() - start_time).total_seconds()
            confidence = self._calculate_confidence(result_data)
            self.execution_count += 1
            self.success_rate = (self.success_rate * (self.execution_count - 1) + 1.0) / self.execution_count
            return AgentResult(
                agent_name=self.name,
                status="success",
                execution_time=execution_time,
                confidence_score=confidence,
                data=result_data,
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Agent {self.name} failed: {str(e)}")
            return AgentResult(
                agent_name=self.name,
                status="failed",
                execution_time=execution_time,
                confidence_score=0.0,
                data={},
                errors=[str(e)],
            )

    async def _process(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def _calculate_confidence(self, result_data: Dict[str, Any]) -> float:
        if not result_data:
            return 0.0
        required_fields = self._get_required_fields()
        present_fields = sum(1 for field in required_fields if field in result_data and result_data[field])
        return present_fields / len(required_fields) if required_fields else 1.0

    def _get_required_fields(self) -> List[str]:
        return []
