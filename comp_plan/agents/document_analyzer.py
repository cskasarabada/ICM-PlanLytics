# comp_plan/agents/document_analyzer.py
import json
from typing import Dict, List, Any
from datetime import datetime

from comp_plan.agents.base import BaseAgent


class DocumentAnalyzerAgent(BaseAgent):
    """Specialized agent for document analysis and structure extraction."""

    def __init__(self):
        super().__init__(
            name="Document Analyzer",
            description="Extracts and structures compensation plan information from documents",
            model_preferences=["gpt-4", "claude-3-sonnet", "gpt-3.5-turbo"],
        )

    async def _process(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        text = inputs.get("text", "")
        template = inputs.get("template", "master")
        prompt = self._build_prompt(text, template)

        from comp_plan.core.prompting import call_llm
        result = call_llm(prompt)

        try:
            parsed_result = json.loads(result)
            return self._enhance_document_analysis(parsed_result, text)
        except json.JSONDecodeError:
            return self._fallback_parse(result, text)

    def _build_prompt(self, text: str, template: str) -> str:
        return f"""
        You are a specialized Document Analysis Agent for compensation plans.

        Your task: Extract and structure ALL relevant information from the document.

        Focus on:
        1. Plan Structure: eligibility, timing, calculations
        2. Key Metrics: quotas, rates, thresholds
        3. Business Rules: conditions, exceptions, overrides
        4. Data Requirements: inputs, integrations, reports
        5. Stakeholder Information: roles, responsibilities

        Template Context: {template}

        Document Text:
        <<<
        {text[:50000]}
        >>>

        Return comprehensive JSON with:
        {{
            "plan_overview": {{"name": "", "type": "", "summary": ""}},
            "plan_structure": [
                {{"component": "", "description": "", "calculation_method": "", "dependencies": []}}
            ],
            "eligibility_criteria": [
                {{"role": "", "requirements": [], "effective_dates": ""}}
            ],
            "calculation_rules": [
                {{"rule_name": "", "formula": "", "conditions": [], "examples": []}}
            ],
            "key_metrics": [
                {{"metric": "", "target": "", "measurement": "", "frequency": ""}}
            ],
            "data_requirements": [
                {{"data_type": "", "source": "", "frequency": "", "format": ""}}
            ],
            "business_rules": [
                {{"rule": "", "condition": "", "action": "", "priority": ""}}
            ],
            "governance": [
                {{"aspect": "", "requirement": "", "owner": "", "frequency": ""}}
            ]
        }}
        """

    def _enhance_document_analysis(self, parsed_result: Dict, original_text: str) -> Dict[str, Any]:
        enhanced = parsed_result.copy()
        enhanced["document_metadata"] = {
            "length": len(original_text),
            "complexity_score": self._calculate_complexity(original_text),
            "key_terms_found": self._extract_key_terms(original_text),
            "analysis_timestamp": datetime.now().isoformat(),
        }
        enhanced["confidence_indicators"] = {
            "calculation_clarity": self._assess_calculation_clarity(parsed_result),
            "completeness_score": self._assess_completeness(parsed_result),
            "consistency_score": self._assess_consistency(parsed_result),
        }
        return enhanced

    def _calculate_complexity(self, text: str) -> float:
        complexity_indicators = [
            "if", "when", "unless", "except", "override", "special", "complex",
            "variable", "depends", "conditional", "multiple", "various",
        ]
        score = sum(text.lower().count(indicator) for indicator in complexity_indicators)
        return min(score / 100.0, 1.0)

    def _extract_key_terms(self, text: str) -> List[str]:
        key_terms = [
            "commission", "bonus", "incentive", "quota", "target", "threshold",
            "rate", "tier", "accelerator", "kicker", "spiff", "draw", "clawback",
        ]
        text_lower = text.lower()
        return [term for term in key_terms if term in text_lower]

    def _assess_calculation_clarity(self, result: Dict) -> float:
        rules = result.get("calculation_rules", [])
        if not rules:
            return 0.0
        with_formula = sum(1 for r in rules if r.get("formula"))
        return with_formula / len(rules) if rules else 0.0

    def _assess_completeness(self, result: Dict) -> float:
        fields = ["plan_structure", "eligibility_criteria", "calculation_rules", "key_metrics"]
        present = sum(1 for f in fields if result.get(f))
        return present / len(fields)

    def _assess_consistency(self, result: Dict) -> float:
        return 0.8  # Placeholder

    def _fallback_parse(self, result: str, text: str) -> Dict[str, Any]:
        return {
            "plan_overview": {"name": "Unknown", "type": "Unknown", "summary": result[:200]},
            "plan_structure": [],
            "document_metadata": {"length": len(text)},
        }

    def _get_required_fields(self) -> List[str]:
        return ["plan_structure", "calculation_rules", "eligibility_criteria"]
