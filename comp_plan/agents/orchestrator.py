# comp_plan/agents/orchestrator.py
from typing import Dict, List, Any
from datetime import datetime

from comp_plan.agents.base import AgentType, AnalysisApproach, BaseAgent
from comp_plan.agents.document_analyzer import DocumentAnalyzerAgent
from comp_plan.agents.risk_assessor import RiskAssessmentAgent
from comp_plan.agents.oracle_mapper import OracleMappingAgent


class AIAgentOrchestrator:
    """Orchestrator for managing multiple AI agents."""

    def __init__(self):
        self.agents = {
            AgentType.DOCUMENT_ANALYZER: DocumentAnalyzerAgent(),
            AgentType.RISK_ASSESSOR: RiskAssessmentAgent(),
            AgentType.ORACLE_MAPPER: OracleMappingAgent(),
        }
        self.execution_history = []

    async def analyze_with_approach(
        self,
        text: str,
        template: str,
        approach: AnalysisApproach,
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        context = context or {}
        start_time = datetime.now()

        workflows = {
            AnalysisApproach.COMPREHENSIVE: [AgentType.DOCUMENT_ANALYZER, AgentType.RISK_ASSESSOR, AgentType.ORACLE_MAPPER],
            AnalysisApproach.QUICK_SCAN: [AgentType.DOCUMENT_ANALYZER, AgentType.RISK_ASSESSOR],
            AnalysisApproach.RISK_FOCUSED: [AgentType.DOCUMENT_ANALYZER, AgentType.RISK_ASSESSOR],
            AnalysisApproach.TECHNICAL_MAPPING: [AgentType.DOCUMENT_ANALYZER, AgentType.ORACLE_MAPPER],
        }

        selected_agents = workflows.get(approach, workflows[AnalysisApproach.COMPREHENSIVE])

        results = {
            "approach": approach.value,
            "execution_metadata": {
                "start_time": start_time.isoformat(),
                "agents_used": [agent.value for agent in selected_agents],
            },
            "agent_results": {},
        }

        current_context = context.copy()

        for agent_type in selected_agents:
            agent = self.agents[agent_type]
            inputs = self._prepare_agent_inputs(agent_type, text, template, results)
            agent_result = await agent.execute(inputs, current_context)

            results["agent_results"][agent_type.value] = {
                "status": agent_result.status,
                "execution_time": agent_result.execution_time,
                "confidence_score": agent_result.confidence_score,
                "data": agent_result.data,
                "errors": agent_result.errors or [],
                "warnings": agent_result.warnings or [],
            }

            if agent_result.status == "success":
                current_context.update(agent_result.data)

        total_time = (datetime.now() - start_time).total_seconds()
        results["execution_metadata"].update({
            "end_time": datetime.now().isoformat(),
            "total_execution_time": total_time,
            "overall_confidence": self._calculate_overall_confidence(results),
            "success_rate": self._calculate_success_rate(results),
        })

        results["consolidated_insights"] = await self._generate_insights(results)
        return results

    def _prepare_agent_inputs(self, agent_type, text, template, previous_results):
        base_inputs = {"text": text, "template": template}
        if agent_type == AgentType.DOCUMENT_ANALYZER:
            return base_inputs
        elif agent_type == AgentType.RISK_ASSESSOR:
            doc_result = previous_results.get("agent_results", {}).get("document_analyzer", {})
            return {"plan_data": doc_result.get("data", {}), "template": template}
        elif agent_type == AgentType.ORACLE_MAPPER:
            doc_result = previous_results.get("agent_results", {}).get("document_analyzer", {})
            return {"plan_structure": doc_result.get("data", {}), "template": template}
        return base_inputs

    def _calculate_overall_confidence(self, results):
        agent_results = results.get("agent_results", {})
        if not agent_results:
            return 0.0
        scores = [r.get("confidence_score", 0.0) for r in agent_results.values() if r.get("status") == "success"]
        return sum(scores) / len(scores) if scores else 0.0

    def _calculate_success_rate(self, results):
        agent_results = results.get("agent_results", {})
        if not agent_results:
            return 0.0
        successful = sum(1 for r in agent_results.values() if r.get("status") == "success")
        return successful / len(agent_results)

    async def _generate_insights(self, results):
        insights = {"key_findings": [], "critical_issues": [], "recommendations": [], "next_steps": []}
        agent_results = results.get("agent_results", {})

        if "document_analyzer" in agent_results:
            doc_data = agent_results["document_analyzer"].get("data", {})
            if doc_data.get("key_metrics"):
                insights["key_findings"].append("Identified key performance metrics and calculation methods")

        if "risk_assessor" in agent_results:
            risk_data = agent_results["risk_assessor"].get("data", {})
            risk_metrics = risk_data.get("risk_metrics", {})
            if risk_metrics.get("risk_level") in ["HIGH", "CRITICAL"]:
                insights["critical_issues"].append(f"High risk level detected: {risk_metrics.get('risk_level')}")

        if "oracle_mapper" in agent_results:
            oracle_data = agent_results["oracle_mapper"].get("data", {})
            if oracle_data.get("implementation_considerations"):
                insights["recommendations"].append("Oracle ICM implementation roadmap generated")

        return insights
