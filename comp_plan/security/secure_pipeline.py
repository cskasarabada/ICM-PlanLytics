from __future__ import annotations

"""Secure Pipeline - wraps compensation plan analysis with inherent PII scrubbing.

PII scrubbing is BUILT INTO every data transfer:
  extract_text(file)
    -> SecurityLayer.scrub_input(text)         # PII scrub document
    -> build_prompt(scrubbed_text, template)
    -> call_llm(prompt)                         # Via configured LLM backend
    -> SecurityLayer.scrub_output(response)     # Scrub LLM output
    -> json.loads -> infer_oracle_objects
    -> scrub_oracle_mapping(analysis)           # Final oracle scrub
    -> return analysis with _security metadata
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

from comp_plan.security.pii_scrubber import (
    SecurityLayer,
    auto_protect,
    generate_pii_warnings,
    generate_pii_warning_summary,
)
from comp_plan.core.parsing import extract_text
from comp_plan.core.prompting import build_prompt, call_llm
from comp_plan.core.mapping_oracle import infer_oracle_objects
from comp_plan.security.oracle_security import scrub_oracle_mapping

logger = logging.getLogger("comp_plan.secure_pipeline")


def run_secure_analysis(
    file_path: Path,
    template: str,
    tenant_id: Optional[str] = None,
    org_id: Optional[str] = None,
    security: Optional[SecurityLayer] = None,
) -> dict[str, Any]:
    """Secured compensation plan analysis with inherent PII scrubbing.

    PII is scrubbed at EVERY stage:
    1. Input document text is scrubbed before LLM sees it
    2. LLM output is scrubbed to catch hallucinated PII
    3. Oracle mapping is deep-scrubbed before export

    Args:
        file_path: Path to .docx, .pdf, or .txt file
        template: Analysis template name
        tenant_id: Optional tenant identifier
        org_id: Optional organization identifier
        security: Optional pre-configured SecurityLayer (uses auto_protect if None)
    """
    # Get or auto-create security layer
    if security is None:
        security = auto_protect(tenant_id or "default")

    # Step 1: Extract text from uploaded document
    text = extract_text(file_path)

    # Step 2: PII scrub the input text (INHERENT - always happens)
    scrubbed_text, scrub_ctx = security.scrub_input(text)

    # Step 3: Build prompt from SCRUBBED text and call LLM
    prompt = build_prompt(scrubbed_text, template)
    raw_response = call_llm(prompt)

    # Step 4: Scrub PII from LLM output (INHERENT - always happens)
    raw_response = security.scrub_output(raw_response)

    # Step 5: Parse JSON
    try:
        analysis = json.loads(raw_response.strip())
    except Exception:
        start = raw_response.find("{")
        end = raw_response.rfind("}")
        if start >= 0 and end > start:
            analysis = json.loads(raw_response[start:end + 1])
        else:
            raise

    analysis["template"] = template
    analysis = infer_oracle_objects(analysis)

    # Step 6: Scrub oracle_mapping (INHERENT - always happens)
    analysis = scrub_oracle_mapping(analysis, security)

    # Attach security metadata
    analysis["_security"] = {
        "pii_scrubbed": scrub_ctx.had_pii,
        "pii_warnings": generate_pii_warnings(scrub_ctx),
        "pii_summary": generate_pii_warning_summary(scrub_ctx),
        "tenant_id": tenant_id,
        "org_id": org_id,
    }

    return analysis
