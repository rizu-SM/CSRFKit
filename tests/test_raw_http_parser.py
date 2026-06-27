"""Tests for the raw HTTP request parser."""

import pytest

from src.parser.raw_http_parser import (
    RawHttpParseError,
    parse_headers,
    parse_raw_http,
    parse_request_line,
    split_head_and_body,
)


# ---------------------------------------------------------------------------
# split_head_and_body
# ---------------------------------------------------------------------------

class TestSplitHeadAndBody:
    """Tests for the head/body splitter."""

    def test_splits_on_crlf_double_newline(self):
        """Windows-style line endings (\r\n\r\n) are handled correctly."""
        raw = "POST /path HTTP/1.1\r\nHost: example.com\r\n\r\nbody=data"
        head, body = split_head_and_body(raw)
        assert "Host: example.com" in head
        assert body == "body=data"

    def test_splits_on_lf_double_newline(self):
        """Unix-style line endings (\n\n) are handled correctly."""
        raw = "POST /path HTTP/1.1\nHost: example.com\n\nbody=data"
        head, body = split_head_and_body(raw)
        assert "Host: example.com" in head
        assert body == "body=data"

    def test_no_body_returns_empty_string(self):
        """A request with no body separator returns an empty body."""
        raw = "GET /path HTTP/1.1\nHost: example.com"
        head, body = split_head_and_body(raw)
        assert head == raw
        assert body == ""

    def test_body_with_double_newline_is_not_split_again(self):
        """The maxsplit=1 argument ensures body double-newlines are preserved."""
        raw = "POST /path HTTP/1.1\n\nfirst paragraph\n\nsecond paragraph"
        head, body = split_head_and_body(raw)
        assert head == "POST /path HTTP/1.1"
        assert body == "first paragraph\n\nsecond paragraph"

    def test_prefers_crlf_over_lf(self):
        """When both styles exist, \r\n\r\n takes priority."""
        raw = "POST /path HTTP/1.1\r\n\r\nbody=1"
        head, body = split_head_and_body(raw)
        assert body == "body=1"


# ---------------------------------------------------------------------------
# parse_request_line
# ---------------------------------------------------------------------------

class TestParseRequestLine:
    """Tests for the first-line parser."""

    def test_parses_method_and_path(self):
        method, url = parse_request_line("POST /change-email HTTP/1.1")
        assert method == "POST"
        assert url == "/change-email"

    def test_parses_absolute_url(self):
        method, url = parse_request_line("GET https://example.com/profile HTTP/1.1")
        assert method == "GET"
        assert url == "https://example.com/profile"

    def test_ignores_http_version(self):
        """HTTP version (HTTP/1.1) is discarded - we only need method and URL."""
        method, url = parse_request_line("DELETE /resource HTTP/2")
        assert method == "DELETE"
        assert url == "/resource"

    def test_raises_on_missing_url(self):
        """A line with only a method (no URL) raises RawHttpParseError."""
        with pytest.raises(RawHttpParseError, match="method and URL"):
            parse_request_line("GET")

    def test_raises_on_empty_line(self):
        """An empty or blank line raises RawHttpParseError."""
        with pytest.raises(RawHttpParseError):
            parse_request_line("   ")


# ---------------------------------------------------------------------------
# parse_headers
# ---------------------------------------------------------------------------

class TestParseHeaders:
    """Tests for the header-line-to-dict parser."""

    def test_parses_basic_headers(self):
        lines = ["Host: example.com", "Content-Type: application/json"]
        headers = parse_headers(lines)
        assert headers["Host"] == "example.com"
        assert headers["Content-Type"] == "application/json"

    def test_skips_blank_lines(self):
        """Blank lines between headers are ignored without raising an error."""
        lines = ["Host: example.com", "", "Accept: */*"]
        headers = parse_headers(lines)
        assert len(headers) == 2

    def test_strips_whitespace_from_keys_and_values(self):
        lines = ["  Host  :   example.com  "]
        headers = parse_headers(lines)
        assert headers["Host"] == "example.com"

    def test_header_value_with_colon(self):
        """Values containing colons (e.g. port numbers) are preserved."""
        lines = ["Host: example.com:8080"]
        headers = parse_headers(lines)
        assert headers["Host"] == "example.com:8080"

    def test_raises_on_invalid_header_line(self):
        """A line without a colon separator raises RawHttpParseError."""
        with pytest.raises(RawHttpParseError, match="Invalid header"):
            parse_headers(["ThisIsNotAHeader"])


# ---------------------------------------------------------------------------
# parse_raw_http  (end-to-end)
# ---------------------------------------------------------------------------

class TestParseRawHttp:
    """End-to-end tests for the main parser function."""

    def test_parses_full_post_request(self):
        raw = (
            "POST /change-email HTTP/1.1\n"
            "Host: example.com\n"
            "Content-Type: application/x-www-form-urlencoded\n"
            "\n"
            "email=test@example.com&display_name=Test+User"
        )
        req = parse_raw_http(raw)
        assert req.method == "POST"
        assert req.url == "/change-email"
        assert req.host == "example.com"
        assert req.form_fields["email"] == "test@example.com"
        assert req.form_fields["display_name"] == "Test User"

    def test_parses_get_request_without_body(self):
        raw = "GET /profile HTTP/1.1\nHost: example.com"
        req = parse_raw_http(raw)
        assert req.method == "GET"
        assert req.body == ""
        assert req.form_fields == {}

    def test_full_url_is_built_from_host_and_path(self):
        raw = "POST /change-email HTTP/1.1\nHost: example.com\n\nemail=a@b.com"
        req = parse_raw_http(raw)
        assert req.full_url() == "https://example.com/change-email"

    def test_method_is_uppercased(self):
        """Methods in any casing are normalized to uppercase."""
        raw = "post /path HTTP/1.1\nHost: example.com"
        req = parse_raw_http(raw)
        assert req.method == "POST"

    def test_raises_on_empty_input(self):
        with pytest.raises(RawHttpParseError, match="empty"):
            parse_raw_http("   ")

    def test_raises_on_blank_string(self):
        with pytest.raises(RawHttpParseError):
            parse_raw_http("")
