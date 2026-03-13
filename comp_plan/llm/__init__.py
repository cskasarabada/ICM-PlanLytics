"""comp_plan.llm - Pluggable LLM backend.

MicroLLM (siraimmicro) is optional. Set COMP_PLAN_LLM_BACKEND=microllm to plug it in.
"""

from comp_plan.llm.llm_adapter import call_llm, ICM_SYSTEM_ROLE

__all__ = ["call_llm", "ICM_SYSTEM_ROLE"]
