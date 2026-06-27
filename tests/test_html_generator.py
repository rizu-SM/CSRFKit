"""Tests for generated HTML PoC output."""

import pytest

from src.core.request_model import HttpRequest
from src.generator.html_generator import (
    form_method,
    generate_html_poc,
    render_hidden_fields,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_request(
    method: str = "POST",
    url: str = "https://example.com/change-email",
    headers: dict | None = None,
    body: str = "",
    form_fields: dict | None = None,
) -> HttpRequest:
    """Build an HttpRequest with sensible defaults for testing."""
    return HttpRequest(
        method=method,
        url=url,
        headers=headers or {},
        body=body,
        form_fields=form_fields or {},
    )


# ---------------------------------------------------------------------------
# form_method
# ---------------------------------------------------------------------------

class TestFormMethod:
    """Tests for the HTTP method normalizer."""

    def test_returns_post_for_post(self):
        assert form_method("POST") == "POST"

    def test_returns_get_for_get(self):
        assert form_method("GET") == "GET"

    def test_returns_post_for_put(self):
        """PUT is not supported by HTML forms — falls back to POST."""
        assert form_method("PUT") == "POST"

    def test_returns_post_for_delete(self):
        """DELETE is not supported by HTML forms — falls back to POST."""
        assert form_method("DELETE") == "POST"

    def test_is_case_insensitive(self):
        assert form_method("get") == "GET"
        assert form_method("post") == "POST"


# ---------------------------------------------------------------------------
# render_hidden_fields
# ---------------------------------------------------------------------------

class TestRenderHiddenFields:
    """Tests for the hidden input renderer."""

    def test_renders_single_field(self):
        html = render_hidden_fields({"email": "test@example.com"})
        assert 'name="email"' in html
        assert 'value="test@example.com"' in html
        assert 'type="hidden"' in html

    def test_renders_multiple_fields(self):
        html = render_hidden_fields({
            "email": "a@b.com",
            "name": "Alice",
        })
        assert 'name="email"' in html
        assert 'name="name"' in html

    def test_each_field_on_its_own_line(self):
        html = render_hidden_fields({"a": "1", "b": "2"})
        lines = html.splitlines()
        assert len(lines) == 2

    def test_escapes_special_characters_in_name(self):
        """Field names with < > & " are HTML-escaped."""
        html = render_hidden_fields({"<script>": "x"})
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_escapes_special_characters_in_value(self):
        """Field values with quotes are escaped so they cannot break the HTML."""
        html = render_hidden_fields({"field": '"quoted"'})
        assert '"quoted"' not in html
        assert "&quot;quoted&quot;" in html

    def test_returns_empty_string_for_no_fields(self):
        assert render_hidden_fields({}) == ""


# ---------------------------------------------------------------------------
# generate_html_poc  (end-to-end)
# ---------------------------------------------------------------------------

class TestGenerateHtmlPoc:
    """End-to-end tests for the PoC HTML generator."""

    def test_form_action_is_full_url(self):
        req = make_request(
            url="/change-email",
            headers={"Host": "example.com"},
            form_fields={"email": "a@b.com"},
        )
        html = generate_html_poc(req)
        assert 'action="https://example.com/change-email"' in html

    def test_form_method_is_post(self):
        req = make_request(method="POST", form_fields={"x": "1"})
        html = generate_html_poc(req)
        assert 'method="POST"' in html

    def test_form_method_is_get(self):
        req = make_request(method="GET")
        html = generate_html_poc(req)
        assert 'method="GET"' in html

    def test_hidden_fields_are_present(self):
        req = make_request(form_fields={"email": "a@b.com", "name": "Alice"})
        html = generate_html_poc(req)
        assert 'name="email"' in html
        assert 'name="name"' in html

    def test_auto_submit_script_is_present(self):
        """The page must auto-submit the form via JavaScript."""
        req = make_request()
        html = generate_html_poc(req)
        assert "document.forms[0].submit()" in html

    def test_html_is_valid_doctype(self):
        req = make_request()
        html = generate_html_poc(req)
        assert html.strip().startswith("<!doctype html>")

    def test_url_special_characters_are_escaped(self):
        """Ampersands or quotes in the URL are safely escaped."""
        req = make_request(url='https://example.com/path?a=1&b="x"')
        html = generate_html_poc(req)
        # Raw & and " should not appear unescaped inside an attribute
        assert 'action="https://example.com/path?a=1&amp;b=&quot;x&quot;"' in html
