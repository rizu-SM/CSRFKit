"""Request body parser.

Role:
    Parse request bodies into key/value fields that can be placed into
    generated HTML forms.

Initial target:
    application/x-www-form-urlencoded

Later targets:
    multipart/form-data
    text/plain form submissions
"""

from urllib.parse import parse_qsl


FORM_URLENCODED = "application/x-www-form-urlencoded"


def is_form_urlencoded(content_type: str) -> bool:
    """Return True when the content type is HTML form compatible."""

    return content_type.lower().split(";", 1)[0].strip() == FORM_URLENCODED


def parse_form_urlencoded(body: str) -> dict[str, str]:
    """Parse an application/x-www-form-urlencoded body into form fields."""

    if not body.strip():
        return {}

    return dict(parse_qsl(body, keep_blank_values=True))


def parse_body(body: str, content_type: str) -> dict[str, str]:
    """Parse a request body when its content type is supported."""

    if is_form_urlencoded(content_type):
        return parse_form_urlencoded(body)

    return {}
