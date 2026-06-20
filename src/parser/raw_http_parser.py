"""Parser for raw HTTP requests.

Role:
    Convert a pasted HTTP request into the shared HttpRequest model.

Example input:
    POST /change-email HTTP/1.1
    Host: example.com
    Content-Type: application/x-www-form-urlencoded

    email=test@example.com
"""

from src.core.request_model import HttpRequest
from src.parser.body_parser import parse_body


class RawHttpParseError(ValueError):
    """Raised when raw HTTP input cannot be parsed."""


def parse_raw_http(raw_request: str) -> HttpRequest:
    """Parse a raw HTTP request string into an HttpRequest."""

    cleaned_request = raw_request.strip()

    if not cleaned_request:
        raise RawHttpParseError("Raw HTTP request is empty.")

    head, body = split_head_and_body(cleaned_request)
    lines = head.splitlines()

    method, url = parse_request_line(lines[0])
    headers = parse_headers(lines[1:])
    content_type = headers.get("Content-Type", "")
    form_fields = parse_body(body, content_type)

    return HttpRequest(
        method=method,
        url=url,
        headers=headers,
        body=body,
        form_fields=form_fields,
    )


def split_head_and_body(raw_request: str) -> tuple[str, str]:
    """Split a raw request into header text and body text."""

    if "\r\n\r\n" in raw_request:
        return raw_request.split("\r\n\r\n", 1)

    if "\n\n" in raw_request:
        return raw_request.split("\n\n", 1)

    return raw_request, ""


def parse_request_line(request_line: str) -> tuple[str, str]:
    """Parse the first HTTP request line."""

    parts = request_line.split()

    if len(parts) < 2:
        raise RawHttpParseError("Request line must include a method and URL.")

    method = parts[0]
    url = parts[1]

    return method, url


def parse_headers(header_lines: list[str]) -> dict[str, str]:
    """Parse HTTP header lines into a dictionary."""

    headers: dict[str, str] = {}

    for line in header_lines:
        if not line.strip():
            continue

        if ":" not in line:
            raise RawHttpParseError(f"Invalid header line: {line}")

        name, value = line.split(":", 1)
        headers[name.strip()] = value.strip()

    return headers
