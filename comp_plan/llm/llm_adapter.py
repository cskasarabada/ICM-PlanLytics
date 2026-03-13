"""LLM Adapter - Pluggable LLM backend for comp_plan.

By default uses the built-in OpenAI/Ollama backends from prompting.py.
If MicroLLM (siraimmicro) is installed, it can be plugged in as the backend.

To plug in MicroLLM:
    pip install siraimmicro
    Set env: COMP_PLAN_LLM_BACKEND=microllm

To use built-in backends:
    Set env: LLM_BACKEND=openai (or ollama, stub)
"""

import logging
import os
from typing import Optional

logger = logging.getLogger("comp_plan.llm_adapter")

# ICM-PlanLytics system prompt
ICM_SYSTEM_ROLE = (
    "You are an Incentive Compensation Automation Analyst. "
    "Extract plan mechanics, risks, stakeholder questions, and translate them into "
    "vendor-neutral requirements, then map to Oracle ICM objects. "
    "Return compact JSON ONLY that matches required schema fields. Do not invent facts."
)

# Lazy-initialized backend
_llm_backend = None


def _get_backend():
    """Get the configured LLM backend. Supports MicroLLM plug-in or built-in backends."""
    global _llm_backend

    if _llm_backend is not None:
        return _llm_backend

    backend_type = os.getenv("COMP_PLAN_LLM_BACKEND", "builtin").lower()

    if backend_type == "microllm":
        try:
            from siraimmicro.micro_llm import MicroLLM, MicroLLMConfig

            provider = os.getenv("SIRAIMMICRO_PROVIDER", os.getenv("LLM_BACKEND", "openai"))
            model = os.getenv("SIRAIMMICRO_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

            _llm_backend = MicroLLM(MicroLLMConfig(
                provider=provider,
                model=model,
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
                api_base=os.getenv("OLLAMA_URL"),
                api_key=os.getenv("OPENAI_API_KEY"),
            ))
            logger.info("MicroLLM plugged in: provider=%s model=%s", provider, model)
            return _llm_backend
        except ImportError:
            logger.warning("COMP_PLAN_LLM_BACKEND=microllm but siraimmicro not installed. Falling back to builtin.")

    # Use built-in backends (flag for call_llm to use prompting.py directly)
    _llm_backend = "builtin"
    return _llm_backend


def call_llm(prompt: str, temperature: Optional[float] = None) -> str:
    """Call the configured LLM backend.

    If MicroLLM is plugged in, uses it. Otherwise falls back to
    built-in OpenAI/Ollama/stub backends from comp_plan.core.prompting.
    """
    backend = _get_backend()

    if backend == "builtin":
        # Fall through to the built-in backends in prompting.py
        # This import is intentionally deferred to avoid circular imports
        from comp_plan.core.prompting import (
            _call_openai, _call_ollama, _call_stub,
            LLM_BACKEND, TEMPERATURE,
        )
        try:
            if LLM_BACKEND == "openai":
                return _call_openai(prompt)
            if LLM_BACKEND == "ollama":
                return _call_ollama(prompt)
            return _call_stub(prompt)
        except Exception:
            return _call_stub(prompt)

    # MicroLLM backend
    try:
        kwargs = {}
        if temperature is not None:
            kwargs["temperature"] = temperature
        return backend.complete(
            prompt=prompt,
            system=ICM_SYSTEM_ROLE,
            **kwargs,
        )
    except Exception as e:
        logger.warning("MicroLLM call failed, falling back to stub: %s", e)
        from comp_plan.core.prompting import _call_stub
        return _call_stub(prompt)
