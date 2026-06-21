"""CSRF compatibility analyzer.

Role:
    Inspect a normalized HttpRequest and decide whether it can be represented
    as a browser-submitable CSRF PoC.

This module should also produce warnings for requests that may not work well,
such as JSON APIs, bearer tokens, or required custom headers.
"""

from dataclasses import dataclass, field

from src.core.request_model import HttpRequest
from src.core.validators import (
    has_absolute_url,
    has_unsafe_browser_headers,
    is_form_compatible_content_type,
    is_supported_method,
)


@dataclass
class CsrfAnalysis:
    """Result of checking whether a request is suitable for CSRF PoC output."""

    can_generate: bool
    warnings: list[str] = field(default_factory=list)


def analyze_request(request: HttpRequest) -> CsrfAnalysis:
    """Analyze a request and return generation status plus warnings."""

    warnings: list[str] = []

    if not is_supported_method(request.method):
        warnings.append(
            f"HTTP method {request.method} is not supported by normal HTML forms."
        )

    if not has_absolute_url(request):
        warnings.append(
            "Request target is not an absolute URL and no Host header was found."
        )

    if not is_form_compatible_content_type(request.content_type):
        warnings.append(
            f"Content-Type {request.content_type or '(missing)'} is not form-compatible."
        )

    if has_unsafe_browser_headers(request):
        warnings.append(
            "Request includes headers that plain HTML forms cannot set."
        )

    if request.method == "POST" and request.content_type and not request.form_fields:
        warnings.append(
            "POST request body did not produce form fields for the PoC."
        )

    can_generate = not warnings

    return CsrfAnalysis(
        can_generate=can_generate,
        warnings=warnings,
    )
