from __future__ import annotations

"""PII Scrubber - Detects and masks PII/credentials in text.

Built-in to comp_plan so PII scrubbing is inherent to ALL data transfers.
Every document, LLM call, and export passes through this layer automatically.

Supports: SSN, credit cards, emails, phones, API keys, passwords,
EIN, IBAN, SWIFT, bank accounts, company names, and custom patterns.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from pydantic import BaseModel, Field as PydanticField

logger = logging.getLogger(__name__)


# --- PII Pattern Definitions ---

@dataclass
class PIIPattern:
    """A single PII detection pattern."""
    name: str
    pattern: re.Pattern
    placeholder_prefix: str
    description: str = ""

    def __post_init__(self):
        if isinstance(self.pattern, str):
            self.pattern = re.compile(self.pattern)


_BUILTIN_PATTERNS: list[PIIPattern] = [
    PIIPattern(name="ssn", pattern=re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), placeholder_prefix="[SSN", description="US Social Security Number"),
    PIIPattern(name="ssn_no_dash", pattern=re.compile(r"\b(?<!\d)\d{9}(?!\d)\b"), placeholder_prefix="[SSN", description="US SSN without dashes"),
    PIIPattern(name="credit_card", pattern=re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"), placeholder_prefix="[CREDIT_CARD", description="Credit card number"),
    PIIPattern(name="email", pattern=re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), placeholder_prefix="[EMAIL", description="Email address"),
    PIIPattern(name="phone_us", pattern=re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"), placeholder_prefix="[PHONE", description="US phone number"),
    PIIPattern(name="ip_address", pattern=re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"), placeholder_prefix="[IP_ADDR", description="IPv4 address"),
    PIIPattern(name="aws_access_key", pattern=re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"), placeholder_prefix="[AWS_KEY", description="AWS access key ID"),
    PIIPattern(name="aws_secret_key", pattern=re.compile(r"\b[A-Za-z0-9/+=]{40}\b"), placeholder_prefix="[AWS_SECRET", description="AWS secret access key"),
    PIIPattern(name="api_key_generic", pattern=re.compile(r"\b(?:sk-|pk_live_|pk_test_|rk_live_|rk_test_|Bearer\s+)[A-Za-z0-9_-]{20,}\b"), placeholder_prefix="[API_KEY", description="Generic API key"),
    PIIPattern(name="password_in_url", pattern=re.compile(r"://[^:]+:([^@]+)@"), placeholder_prefix="[CREDENTIAL", description="Password in URL"),
    PIIPattern(name="password_field", pattern=re.compile(r'(?i)(?:password|passwd|pwd|secret|token|api_key|apikey|access_key)\s*[:=]\s*["\']?([^\s"\']{4,})["\']?'), placeholder_prefix="[CREDENTIAL", description="Password/secret field"),
]

_CONSULTING_PATTERNS: list[PIIPattern] = [
    PIIPattern(name="us_ein", pattern=re.compile(r"\b\d{2}-\d{7}\b"), placeholder_prefix="[EIN", description="US Employer Identification Number"),
    PIIPattern(name="iban", pattern=re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}(?:[A-Z0-9]{0,18})\b"), placeholder_prefix="[IBAN", description="IBAN"),
    PIIPattern(name="swift_bic", pattern=re.compile(r"\b[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b"), placeholder_prefix="[SWIFT", description="SWIFT/BIC bank code"),
    PIIPattern(name="dollar_amount_large", pattern=re.compile(r"\$\s?\d{1,3}(?:,\d{3})+(?:\.\d{2})?(?:\s?(?:M|MM|B|K|million|billion))?\b"), placeholder_prefix="[DEAL_VALUE", description="Large dollar amounts"),
    PIIPattern(name="routing_number", pattern=re.compile(r"\b(?:routing|ABA)[:\s#]*\d{9}\b"), placeholder_prefix="[ROUTING", description="US bank routing number"),
    PIIPattern(name="account_number", pattern=re.compile(r"\b(?:account|acct)[:\s#]*\d{8,17}\b"), placeholder_prefix="[ACCOUNT", description="Bank account number"),
]


@dataclass
class ScrubContext:
    """Tracks what was scrubbed, enabling reversible masking."""
    replacements: dict[str, str] = field(default_factory=dict)
    pattern_counts: dict[str, int] = field(default_factory=dict)
    had_pii: bool = False
    client_replacements: dict[str, str] = field(default_factory=dict)

    def merge(self, other: "ScrubContext") -> None:
        self.replacements.update(other.replacements)
        self.client_replacements.update(other.client_replacements)
        for k, v in other.pattern_counts.items():
            self.pattern_counts[k] = self.pattern_counts.get(k, 0) + v
        if other.had_pii:
            self.had_pii = True


# --- Company Name Detection ---

_COMPANY_SUFFIXES = re.compile(
    r"\b([A-Z][A-Za-z&\'\-]+"
    r"(?:\s+(?:and|&)\s+[A-Z][A-Za-z&\'\-]+)*"
    r")\s+"
    r"(Corp(?:oration)?|Inc(?:orporated)?|LLC|Ltd|L\.L\.C\."
    r"|Group|Partners|LLP|PLC|GmbH|S\.A\.|Co(?:mpany)?\.?"
    r"|Associates|Consulting|Solutions|Enterprises|International)"
    r"\b\.?",
    re.MULTILINE,
)


def _mask_unknown_companies(text: str, counters: dict[str, int]) -> tuple[str, dict[str, str]]:
    """Detect company names by suffix and mask them."""
    client_map: dict[str, str] = {}
    matches = list(_COMPANY_SUFFIXES.finditer(text))
    if not matches:
        return text, client_map
    for match in reversed(matches):
        full_name = match.group(0).rstrip(".")
        count = counters.get("COMPANY", 0) + 1
        counters["COMPANY"] = count
        placeholder = f"[COMPANY_{count}]"
        client_map[placeholder] = full_name
        text = text[:match.start()] + placeholder + text[match.end():]
    return text, client_map


class SecurityLayer:
    """PII masking and credential scrubbing layer.

    Sits between user input and LLM calls to ensure no sensitive data
    reaches the model. Supports reversible masking for authorized restore.
    """

    def __init__(
        self,
        patterns: list[PIIPattern] | None = None,
        enable_reversible: bool = True,
        custom_patterns: list[PIIPattern] | None = None,
        scrub_output_enabled: bool = True,
        mask_client_names: bool = False,
    ):
        self.patterns = list(patterns or _BUILTIN_PATTERNS)
        if custom_patterns:
            self.patterns.extend(custom_patterns)
        self.enable_reversible = enable_reversible
        self.scrub_output_enabled = scrub_output_enabled
        self.mask_client_names = mask_client_names
        self._counters: dict[str, int] = {}
        self._client_counters: dict[str, int] = {}

    def _next_placeholder(self, prefix: str, pattern_name: str) -> str:
        count = self._counters.get(pattern_name, 0) + 1
        self._counters[pattern_name] = count
        return f"{prefix}_{count}]"

    def scrub_text(self, text: str) -> tuple[str, ScrubContext]:
        """Scrub all PII from text. Returns (scrubbed_text, context_for_restore)."""
        ctx = ScrubContext()
        if not text:
            return text, ctx

        self._counters = {}
        self._client_counters = {}

        # Phase 1: Company name masking
        if self.mask_client_names:
            text, unknown_map = _mask_unknown_companies(text, self._client_counters)
            if unknown_map:
                ctx.client_replacements.update(unknown_map)
                ctx.had_pii = True
                ctx.pattern_counts["client_name_detected"] = len(unknown_map)

        # Phase 2: PII pattern matching
        for pii_pattern in self.patterns:
            matches = list(pii_pattern.pattern.finditer(text))
            if not matches:
                continue
            ctx.had_pii = True
            ctx.pattern_counts[pii_pattern.name] = ctx.pattern_counts.get(pii_pattern.name, 0) + len(matches)

            for match in reversed(matches):
                original = match.group(0)
                if pii_pattern.name == "password_field" and match.lastindex and match.lastindex >= 1:
                    original_value = match.group(1)
                    placeholder = self._next_placeholder(pii_pattern.placeholder_prefix, pii_pattern.name)
                    if self.enable_reversible:
                        ctx.replacements[placeholder] = original_value
                    start, end = match.span(1)
                    text = text[:start] + placeholder + text[end:]
                elif pii_pattern.name == "password_in_url" and match.lastindex and match.lastindex >= 1:
                    original_value = match.group(1)
                    placeholder = self._next_placeholder(pii_pattern.placeholder_prefix, pii_pattern.name)
                    if self.enable_reversible:
                        ctx.replacements[placeholder] = original_value
                    start, end = match.span(1)
                    text = text[:start] + placeholder + text[end:]
                else:
                    placeholder = self._next_placeholder(pii_pattern.placeholder_prefix, pii_pattern.name)
                    if self.enable_reversible:
                        ctx.replacements[placeholder] = original
                    text = text[:match.start()] + placeholder + text[match.end():]

        if ctx.had_pii:
            logger.info("PII scrubbed: %s", ", ".join(f"{k}={v}" for k, v in ctx.pattern_counts.items()))
        return text, ctx

    def scrub_input(self, text: str) -> tuple[str, ScrubContext]:
        """Scrub PII from input before sending to LLM."""
        return self.scrub_text(text)

    def scrub_output(self, text: str) -> str:
        """Scrub PII from LLM output (one-way, non-reversible)."""
        if not self.scrub_output_enabled or not text:
            return text
        scrubbed, ctx = self.scrub_text(text)
        if ctx.had_pii:
            logger.warning("PII detected in LLM output — scrubbed %s", ctx.pattern_counts)
        return scrubbed

    def restore(self, text: str, ctx: ScrubContext) -> str:
        """Restore original PII values (for authorized users only)."""
        if not self.enable_reversible:
            return text
        for placeholder, original in ctx.replacements.items():
            text = text.replace(placeholder, original)
        for placeholder, original in ctx.client_replacements.items():
            text = text.replace(placeholder, original)
        return text

    def get_scrub_report(self, ctx: ScrubContext) -> dict:
        return {
            "had_pii": ctx.had_pii,
            "patterns_matched": ctx.pattern_counts,
            "total_replacements": sum(ctx.pattern_counts.values()),
            "reversible": self.enable_reversible,
        }


def create_security_layer(
    enable_reversible: bool = True,
    custom_patterns: list[PIIPattern] | None = None,
    scrub_output: bool = True,
    include_consulting: bool = False,
) -> SecurityLayer:
    """Factory to create a SecurityLayer with sensible defaults."""
    patterns = list(_BUILTIN_PATTERNS)
    if include_consulting:
        patterns.extend(_CONSULTING_PATTERNS)
    return SecurityLayer(
        patterns=patterns,
        enable_reversible=enable_reversible,
        custom_patterns=custom_patterns,
        scrub_output_enabled=scrub_output,
    )


def auto_protect(tenant_id: str = "default") -> SecurityLayer:
    """Get a SecurityLayer with maximum protection. Zero-config path."""
    return create_security_layer(enable_reversible=True, scrub_output=True, include_consulting=True)


# --- Human-Readable PII Warnings ---

_FRIENDLY_NAMES: dict[str, str] = {
    "ssn": "a Social Security Number", "ssn_no_dash": "a Social Security Number",
    "credit_card": "a credit card number", "email": "an email address",
    "phone_us": "a phone number", "ip_address": "an IP address",
    "aws_access_key": "an AWS access key", "aws_secret_key": "a secret key",
    "api_key_generic": "an API key or token", "password_in_url": "a password in a URL",
    "password_field": "a password or secret", "client_name_detected": "a company name",
    "us_ein": "a Tax ID (EIN)", "iban": "a bank account number (IBAN)",
    "swift_bic": "a SWIFT/BIC bank code", "dollar_amount_large": "a deal/budget value",
    "routing_number": "a bank routing number", "account_number": "a bank account number",
}


def generate_pii_warnings(ctx: ScrubContext) -> list[str]:
    """Generate plain-English warning messages from a scrub result."""
    if not ctx.had_pii:
        return []
    warnings = []
    seen_friendly = set()
    for pattern_name, count in ctx.pattern_counts.items():
        friendly = _FRIENDLY_NAMES.get(pattern_name, f"sensitive data ({pattern_name})")
        if friendly in seen_friendly:
            continue
        seen_friendly.add(friendly)
        if count == 1:
            warnings.append(f"We detected {friendly} in your input and removed it before processing.")
        else:
            warnings.append(f"We detected {count} instances of {friendly} in your input and removed them before processing.")
    return warnings


def generate_pii_warning_summary(ctx: ScrubContext) -> Optional[str]:
    """Generate a single summary warning string."""
    if not ctx.had_pii:
        return None
    seen = set()
    items = []
    for pattern_name in ctx.pattern_counts:
        friendly = _FRIENDLY_NAMES.get(pattern_name, f"sensitive data ({pattern_name})")
        if friendly not in seen:
            seen.add(friendly)
            items.append(friendly)
    if len(items) == 1:
        return f"Heads up: We removed {items[0]} from your message to protect your client's privacy."
    listed = ", ".join(items[:-1]) + f" and {items[-1]}"
    return f"Heads up: We removed {listed} from your message to protect your client's privacy."


def list_available_patterns(include_consulting: bool = False) -> list[dict[str, str]]:
    """List all builtin PII pattern names and descriptions."""
    patterns = list(_BUILTIN_PATTERNS)
    if include_consulting:
        patterns.extend(_CONSULTING_PATTERNS)
    return [{"name": p.name, "description": p.description} for p in patterns]
