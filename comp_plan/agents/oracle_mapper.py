# comp_plan/agents/oracle_mapper.py
import json
from typing import Dict, List, Any

from comp_plan.agents.base import BaseAgent


class OracleMappingAgent(BaseAgent):
    """Specialized agent for Oracle ICM object mapping."""

    def __init__(self):
        super().__init__(
            name="Oracle ICM Mapper",
            description="Maps compensation requirements to Oracle ICM objects and configuration",
            model_preferences=["gpt-4", "claude-3-sonnet"],
        )

    async def _process(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        plan_structure = inputs.get("plan_structure", {})
        existing_system = context.get("existing_system", None)
        prompt = self._build_oracle_prompt(plan_structure, existing_system)

        from comp_plan.core.prompting import call_llm
        result = call_llm(prompt)

        try:
            parsed_result = json.loads(result)
            return self._enhance_oracle_mapping(parsed_result)
        except json.JSONDecodeError:
            return self._fallback_oracle_mapping(result)

    def _build_oracle_prompt(self, plan_structure: Dict, existing_system: str) -> str:
        return f"""
        You are an Oracle ICM Implementation Specialist.

        Map the compensation plan requirements to Oracle ICM objects and configuration.

        Plan Requirements: {json.dumps(plan_structure, indent=2)}
        Existing System: {existing_system or "Greenfield implementation"}

        Provide detailed Oracle ICM mapping as JSON with:
        participants[], transactions[], credit_rules[], rate_tables[],
        plan_elements[], measurements[], roles_and_positions[],
        reports_and_statements[], implementation_considerations.
        """

    def _enhance_oracle_mapping(self, parsed_result: Dict) -> Dict[str, Any]:
        enhanced = parsed_result.copy()
        enhanced["implementation_roadmap"] = self._generate_implementation_roadmap(parsed_result)
        enhanced["data_model"] = self._recommend_data_model(parsed_result)
        enhanced["integration_points"] = self._identify_integration_points(parsed_result)
        return enhanced

    def _generate_implementation_roadmap(self, result: Dict) -> List[Dict]:
        phases = []
        if result.get("participants"):
            phases.append({"phase": 1, "name": "Participant Setup", "duration": "2 weeks"})
        if result.get("transactions"):
            phases.append({"phase": 2, "name": "Transaction Configuration", "duration": "3 weeks"})
        if result.get("credit_rules"):
            phases.append({"phase": 3, "name": "Credit Rules", "duration": "2 weeks"})
        if result.get("plan_elements"):
            phases.append({"phase": 4, "name": "Plan Elements & Calculations", "duration": "4 weeks"})
        phases.append({"phase": len(phases) + 1, "name": "Testing & UAT", "duration": "3 weeks"})
        return phases

    def _recommend_data_model(self, result: Dict) -> Dict:
        return {
            "source_systems": ["ERP", "HRIS", "CRM"],
            "staging_tables": ["STG_TRANSACTIONS", "STG_PARTICIPANTS"],
            "etl_frequency": "Daily",
        }

    def _identify_integration_points(self, result: Dict) -> List[Dict]:
        return [
            {"system": "ERP", "data": "Transactions/Invoices", "frequency": "Daily"},
            {"system": "HRIS", "data": "Participants/Roles", "frequency": "Weekly"},
            {"system": "CRM", "data": "Opportunities/Quotas", "frequency": "Monthly"},
        ]

    def _fallback_oracle_mapping(self, result: str) -> Dict[str, Any]:
        return {"participants": [], "transactions": [], "credit_rules": [], "plan_elements": []}

    def _get_required_fields(self) -> List[str]:
        return ["participants", "transactions", "credit_rules", "plan_elements"]
