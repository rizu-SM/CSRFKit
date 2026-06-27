"""Tests for request body parsing."""

import pytest

from src.parser.body_parser import (
    is_form_urlencoded,
    parse_body,
    parse_form_urlencoded,
)


# ---------------------------------------------------------------------------
# is_form_urlencoded
# ---------------------------------------------------------------------------

class TestIsFormUrlencoded:
    """Tests for the content-type checker."""

    def test_returns_true_for_exact_match(self):
        assert is_form_urlencoded("application/x-www-form-urlencoded") is True

    def test_returns_true_for_mixed_case(self):
        """Content-Type header values are case-insensitive."""
        assert is_form_urlencoded("Application/X-WWW-Form-Urlencoded") is True

    def test_returns_true_when_charset_present(self):
        """Extra parameters after ; are ignored."""
        assert is_form_urlencoded("application/x-www-form-urlencoded; charset=UTF-8") is True

    def test_returns_false_for_json(self):
        assert is_form_urlencoded("application/json") is False

    def test_returns_false_for_multipart(self):
        assert is_form_urlencoded("multipart/form-data") is False

    def test_returns_false_for_empty_string(self):
        assert is_form_urlencoded("") is False


# ---------------------------------------------------------------------------
# parse_form_urlencoded
# ---------------------------------------------------------------------------

class TestParseFormUrlencoded:
    """Tests for the URL-encoded body decoder."""

    def test_parses_single_field(self):
        result = parse_form_urlencoded("email=test@example.com")
        assert result == {"email": "test@example.com"}

    def test_parses_multiple_fields(self):
        result = parse_form_urlencoded("email=test@example.com&name=Alice")
        assert result["email"] == "test@example.com"
        assert result["name"] == "Alice"

    def test_decodes_plus_as_space(self):
        """The + character in URL encoding represents a space."""
        result = parse_form_urlencoded("display_name=Test+User")
        assert result["display_name"] == "Test User"

    def test_decodes_percent_encoding(self):
        """Percent-encoded characters like %40 (@) are decoded."""
        result = parse_form_urlencoded("email=test%40example.com")
        assert result["email"] == "test@example.com"

    def test_keeps_blank_values(self):
        """Fields with no value (e.g. subscribe=) are kept, not discarded."""
        result = parse_form_urlencoded("subscribe=&email=a@b.com")
        assert result["subscribe"] == ""
        assert result["email"] == "a@b.com"

    def test_returns_empty_dict_for_empty_body(self):
        assert parse_form_urlencoded("") == {}

    def test_returns_empty_dict_for_whitespace_body(self):
        assert parse_form_urlencoded("   ") == {}


# ---------------------------------------------------------------------------
# parse_body  (dispatcher)
# ---------------------------------------------------------------------------

class TestParseBody:
    """Tests for the content-type dispatcher."""

    def test_parses_urlencoded_body(self):
        result = parse_body(
            "email=a@b.com",
            "application/x-www-form-urlencoded",
        )
        assert result["email"] == "a@b.com"

    def test_returns_empty_dict_for_json_body(self):
        """JSON bodies are not yet supported — returns empty dict."""
        result = parse_body('{"email": "a@b.com"}', "application/json")
        assert result == {}

    def test_returns_empty_dict_for_missing_content_type(self):
        result = parse_body("email=a@b.com", "")
        assert result == {}

    def test_returns_empty_dict_for_empty_body_with_valid_content_type(self):
        result = parse_body("", "application/x-www-form-urlencoded")
        assert result == {}
