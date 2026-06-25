"""Parser for cURL commands.

Role:
    Convert a copied cURL command into the shared HttpRequest model.

Typical input (copied from browser DevTools):
    curl 'https://example.com/change-email' \
      -X POST \
      -H 'Host: example.com' \
      -H 'Content-Type: application/x-www-form-urlencoded' \
      --data-raw 'email=test@example.com&display_name=Test+User'
"""

import shlex

from src.core.request_model import HttpRequest
from src.parser.body_parser import parse_body


class CurlParseError(ValueError):
    """Raised when a cURL command cannot be parsed."""


def parse_curl(raw_curl: str) -> HttpRequest:
    """Parse a cURL command string into an HttpRequest.

    Supports the flags commonly produced when copying a request from
    browser DevTools:
        -X / --request    HTTP method
        -H / --header     Request header (can appear multiple times)
        --data-raw        Request body (sent as-is, no extra processing)
        -d / --data       Request body (same handling as --data-raw here)
    """

    cleaned = _normalize_curl(raw_curl)

    try:
        tokens = shlex.split(cleaned)
    except ValueError as exc:
        raise CurlParseError(f"Could not tokenize cURL command: {exc}") from exc

    if not tokens or tokens[0].lower() != "curl":
        raise CurlParseError("Input does not start with 'curl'.")

    url = _extract_url(tokens)
    method, headers, body = _parse_flags(tokens)

    # Infer POST when a body is present but -X was not given.
    if body and method == "GET":
        method = "POST"

    content_type = headers.get("Content-Type", "")
    form_fields = parse_body(body, content_type)

    return HttpRequest(
        method=method,
        url=url,
        headers=headers,
        body=body,
        form_fields=form_fields,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _normalize_curl(raw_curl: str) -> str:
    """Strip line-continuation characters so shlex can tokenize cleanly.

    Browser DevTools wraps long cURL commands across multiple lines using
    a trailing backslash + newline. We collapse those into a single line
    before tokenizing.

    Example:
        "curl 'https://example.com' \\\\\\n  -X POST"
        ->  "curl 'https://example.com'   -X POST"
    """

    # Replace backslash + newline (both \\\r\n and \\\n) with a space.
    cleaned = raw_curl.replace("\\\r\n", " ").replace("\\\n", " ")
    return cleaned.strip()


def _extract_url(tokens: list[str]) -> str:
    """Find the URL from the token list.

    The URL is the first positional argument after 'curl' that does not
    start with a dash (i.e. it is not a flag).

    Example tokens: ["curl", "'https://example.com'", "-X", "POST"]
                                ^--- this one
    """

    for token in tokens[1:]:
        if not token.startswith("-"):
            return token

    raise CurlParseError("No URL found in cURL command.")


def _parse_flags(tokens: list[str]) -> tuple[str, dict[str, str], str]:
    """Walk the token list and collect method, headers, and body.

    Returns:
        method  : HTTP method string (default "GET")
        headers : dict of header name -> header value
        body    : raw body string (empty string if none)
    """

    method = "GET"
    headers: dict[str, str] = {}
    body = ""

    # Use an index-based loop so we can look ahead to the next token
    # when a flag expects a value (e.g. -X POST, -H 'Host: ...')
    i = 1
    while i < len(tokens):
        token = tokens[i]

        if token in ("-X", "--request"):
            # The very next token is the HTTP method.
            i += 1
            if i >= len(tokens):
                raise CurlParseError("Flag -X / --request requires a value.")
            method = tokens[i].upper()

        elif token in ("-H", "--header"):
            # The very next token is a raw header string like "Host: example.com".
            i += 1
            if i >= len(tokens):
                raise CurlParseError("Flag -H / --header requires a value.")
            name, value = _parse_header_string(tokens[i])
            headers[name] = value

        elif token in ("--data-raw", "--data", "-d", "--data-urlencode"):
            # The very next token is the raw body payload.
            i += 1
            if i >= len(tokens):
                raise CurlParseError(f"Flag {token} requires a value.")
            body = tokens[i]

        i += 1

    return method, headers, body


def _parse_header_string(header: str) -> tuple[str, str]:
    """Split a raw 'Name: Value' header string into a (name, value) tuple.

    Example:
        "Content-Type: application/x-www-form-urlencoded"
        -> ("Content-Type", "application/x-www-form-urlencoded")
    """

    if ":" not in header:
        raise CurlParseError(f"Invalid header format (missing ':'): {header}")

    name, value = header.split(":", 1)
    return name.strip(), value.strip()
