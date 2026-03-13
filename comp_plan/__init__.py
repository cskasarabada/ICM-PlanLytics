"""comp_plan - Dedicated Compensation Plan Analysis Module.

Self-contained module for ICM compensation plan analysis with:
- Document parsing (.docx, .pdf, .txt)
- AI-powered analysis with multi-agent orchestration
- Oracle ICM object mapping
- INHERENT PII scrubbing at every data transfer stage
- Excel/HTML/JSON export

MicroLLM (siraimmicro) is OPTIONAL — plug it in by setting:
    COMP_PLAN_LLM_BACKEND=microllm

Without MicroLLM, uses built-in OpenAI/Ollama/stub backends.

Usage:
    from comp_plan import run_analysis, run_secure_analysis
    from comp_plan.security import auto_protect, SecurityLayer
    from comp_plan.agents import AIAgentOrchestrator, AnalysisApproach
"""

__version__ = "1.0.0"

from comp_plan.core.pipeline import run_analysis
from comp_plan.core.parsing import extract_text
from comp_plan.core.prompting import build_prompt, call_llm
from comp_plan.core.mapping_oracle import infer_oracle_objects
from comp_plan.core.exports import to_excel, simple_html_summary, to_pdf
from comp_plan.security.secure_pipeline import run_secure_analysis
from comp_plan.security.oracle_security import scrub_oracle_mapping, prepare_oracle_export
from comp_plan.security.pii_scrubber import (
    SecurityLayer, auto_protect, create_security_layer,
    generate_pii_warnings, generate_pii_warning_summary,
)
from comp_plan.config import CompPlanConfig, get_config

__all__ = [
    # Core analysis
    "run_analysis", "run_secure_analysis",
    "extract_text", "build_prompt", "call_llm",
    "infer_oracle_objects",
    # Exports
    "to_excel", "simple_html_summary", "to_pdf",
    # Security (inherent)
    "SecurityLayer", "auto_protect", "create_security_layer",
    "scrub_oracle_mapping", "prepare_oracle_export",
    "generate_pii_warnings", "generate_pii_warning_summary",
    # Config
    "CompPlanConfig", "get_config",
]
