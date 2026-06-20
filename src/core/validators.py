"""Validation helpers.

Role:
    Keep small reusable checks in one place.

Examples:
    - Is the HTTP method supported?
    - Is the target URL valid?
    - Is the content type form-compatible?
"""

from src.core.request_model import HttpRequest
from src.parser.body_parser import FORM_URLENCODED


SUPPORTED_METHODS = {"GET", "POST"}
FORM_COMPATIBLE_CONTENT_TYPES = {
    "",
    FORM_URLENCODED,
    "multipart/form-data",
    "text/plain",
}
UNSAFE_BROWSER_HEADERS = {
    "authorization",
    "x-csrf-token",
    "x-requested-with",
}


def is_supported_method(method: str) -> bool:
    """Return True when the method can be represented by an HTML form."""

    return method.upper().strip() in SUPPORTED_METHODS


def has_absolute_url(request: HttpRequest) -> bool:
    """Return True when the request has or can build an absolute URL."""

    return request.full_url().startswith(("http://", "https://"))


def is_form_compatible_content_type(content_type: str) -> bool:
    """Return True when a browser form can naturally submit this content type."""

    normalized = content_type.lower().split(";", 1)[0].strip()
    return normalized in FORM_COMPATIBLE_CONTENT_TYPES


def has_unsafe_browser_headers(request: HttpRequest) -> bool:
    """Return True when the request uses headers plain HTML forms cannot set."""

    request_header_names = {name.lower() for name in request.headers}
    return bool(request_header_names & UNSAFE_BROWSER_HEADERS)
