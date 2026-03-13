from __future__ import annotations

"""Oracle Data Security - scrubs PII from oracle_mapping before export.

LLMs may hallucinate sample data containing PII (employee names, emails,
SSNs) into the oracle_mapping configuration. This module provides two
layers of protection:

1. scrub_oracle_mapping() - inline scrub during analysis
2. prepare_oracle_export() - final verification before sending to Oracle
"""

import json
import logging
from typing import Any

from comp_plan.security.pii_scrubber import SecurityLayer, auto_protect

logger = logging.getLogger("comp_plan.oracle_security")


def scrub_oracle_mapping(analysis: dict[str, Any], security: SecurityLayer) -> dict[str, Any]:
    """Deep-scrub the oracle_mapping section of an analysis result.

    Serializes oracle_mapping to JSON, runs PII scrubbing, then deserializes.
    """
    om = analysis.get("oracle_mapping")
    if not om:
        return analysis

    om_json = json.dumps(om)
    scrubbed_json, ctx = security.scrub_input(om_json)

    if ctx.had_pii:
        logger.warning("PII found in oracle_mapping and scrubbed: %s", dict(ctx.pattern_counts))
        try:
            analysis["oracle_mapping"] = json.loads(scrubbed_json)
        except json.JSONDecodeError:
            logger.error("Failed to parse scrubbed oracle_mapping JSON, keeping original")

    return analysis


def prepare_oracle_export(analysis: dict[str, Any], security: SecurityLayer = None) -> dict[str, Any]:
    """Prepare analysis data for transmission to Oracle ICM systems.

    Called BEFORE any data leaves to Oracle. Performs:
    1. Strip internal metadata (_security key)
    2. Deep scrub of oracle_mapping
    3. Verification that no PII remains
    """
    if security is None:
        security = auto_protect()

    # Remove internal security metadata
    export = {k: v for k, v in analysis.items() if not k.startswith("_")}

    # Deep scrub
    export = scrub_oracle_mapping(export, security)

    # Verification pass (belt and suspenders)
    export_json = json.dumps(export)
    _, verify_ctx = security.scrub_input(export_json)
    if verify_ctx.had_pii:
        logger.critical(
            "PII STILL PRESENT after scrub in oracle export: %s",
            dict(verify_ctx.pattern_counts),
        )

    return export
