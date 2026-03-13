# comp_plan/agents/risk_assessor.py
import json
from typing import Dict, List, Any

from comp_plan.agents.base import BaseAgent


class RiskAssessmentAgent(BaseAgent):
    """Specialized agent for identifying risks and compliance issues."""

    def __init__(self):
        super().__init__(
            name="Risk Assessment",
            description="Identifies compliance, operational, and financial risks in compensation plans",
            model_preferences=["claude-3-sonnet", "gpt-4", "gpt-3.5-turbo"],
        )

    async def _process(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        plan_data = inputs.get("plan_data", {})
        industry = context.get("industry", "general")
        region = context.get("region", "US")
        prompt = self._build_risk_prompt(plan_data, industry, region)

        from comp_plan.core.prompting import call_llm
        result = call_llm(prompt)

        try:
            parsed_result = json.loads(result)
            return self._enhance_risk_analysis(parsed_result, plan_data)
        except json.JSONDecodeError:
            return self._fallback_risk_analysis(result)

    def _build_risk_prompt(self, plan_data: Dict, industry: str, region: str) -> str:
        return f"""
        You are a Risk Assessment Specialist for compensation plans.

        Analyze the following plan for ALL types of risks:

        1. COMPLIANCE RISKS: Regulatory violations (SOX, securities laws), tax, labor law
        2. OPERATIONAL RISKS: Data accuracy, system integration, manual calculation
        3. FINANCIAL RISKS: Budget overruns, calculation errors, gaming potential
        4. STRATEGIC RISKS: Misaligned incentives, talent retention issues

        Plan Data: {json.dumps(plan_data, indent=2)}
        Industry: {industry}
        Region: {region}

        Return detailed JSON with compliance_risks[], operational_risks[], financial_risks[],
        strategic_risks[], and risk_summary with overall_risk_score.
        """

    def _enhance_risk_analysis(self, parsed_result: Dict, plan_data: Dict) -> Dict[str, Any]:
        enhanced = parsed_result.copy()
        enhanced["risk_metrics"] = self._calculate_risk_metrics(parsed_result)
        enhanced["action_plan"] = self._generate_action_plan(parsed_result)
        return enhanced

    def _calculate_risk_metrics(self, risks: Dict) -> Dict:
        all_risks = []
        for category in ["compliance_risks", "operational_risks", "financial_risks", "strategic_risks"]:
            all_risks.extend(risks.get(category, []))

        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for risk in all_risks:
            severity = risk.get("severity", "medium")
            if severity in severity_counts:
                severity_counts[severity] += 1

        risk_score = (
            severity_counts["critical"] * 4
            + severity_counts["high"] * 3
            + severity_counts["medium"] * 2
            + severity_counts["low"] * 1
        ) / max(len(all_risks), 1)

        return {
            "total_risks": len(all_risks),
            "severity_distribution": severity_counts,
            "weighted_risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score),
        }

    def _get_risk_level(self, score: float) -> str:
        if score >= 3.5:
            return "CRITICAL"
        elif score >= 2.5:
            return "HIGH"
        elif score >= 1.5:
            return "MEDIUM"
        return "LOW"

    def _generate_action_plan(self, risks: Dict) -> List[str]:
        actions = []
        for category in ["compliance_risks", "operational_risks", "financial_risks"]:
            for risk in risks.get(category, []):
                for mitigation in risk.get("mitigation_strategies", []):
                    actions.append(mitigation)
        return actions[:10]

    def _fallback_risk_analysis(self, result: str) -> Dict[str, Any]:
        return {
            "compliance_risks": [],
            "operational_risks": [],
            "financial_risks": [],
            "strategic_risks": [],
            "risk_summary": {"overall_risk_score": 0.0},
        }

    def _get_required_fields(self) -> List[str]:
        return ["compliance_risks", "operational_risks", "financial_risks", "strategic_risks"]
