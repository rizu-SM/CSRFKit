"""HTML CSRF PoC generator.

Role:
    Convert a normalized HttpRequest into an HTML proof-of-concept file.

Initial output:
    A simple auto-submitting form with hidden inputs.
"""

from html import escape

from src.core.request_model import HttpRequest
from src.generator.templates import HIDDEN_INPUT_TEMPLATE, HTML_POC_TEMPLATE


def generate_html_poc(request: HttpRequest) -> str:
    """Generate an auto-submitting HTML CSRF PoC."""

    return HTML_POC_TEMPLATE.format(
        action=escape(request.full_url(), quote=True),
        method=escape(form_method(request.method), quote=True),
        fields=render_hidden_fields(request.form_fields),
    )


def form_method(method: str) -> str:
    """Return an HTML form method supported by browsers."""

    normalized = method.upper().strip()

    if normalized == "GET":
        return "GET"

    return "POST"


def render_hidden_fields(fields: dict[str, str]) -> str:
    """Render hidden input elements for parsed form fields."""

    return "\n".join(
        HIDDEN_INPUT_TEMPLATE.format(
            name=escape(name, quote=True),
            value=escape(value, quote=True),
        )
        for name, value in fields.items()
    )
