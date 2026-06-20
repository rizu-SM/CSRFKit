"""Shared request data model.

Role:
    Define the normalized HttpRequest object used by every parser and
    generator module.

All input formats should become this model before analysis or output.
"""

from dataclasses import dataclass, field
from urllib.parse import urljoin


@dataclass
class HttpRequest:
    """Normalized HTTP request used across the application."""

    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    form_fields: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.method = self.method.upper().strip()
        self.url = self.url.strip()
        self.headers = {
            key.strip(): value.strip()
            for key, value in self.headers.items()
        }

    @property
    def content_type(self) -> str:
        """Return the request content type without parameters."""

        raw_content_type = self.get_header("Content-Type")
        return raw_content_type.split(";", 1)[0].strip().lower()

    @property
    def host(self) -> str:
        """Return the Host header value, if present."""

        return self.get_header("Host")

    def get_header(self, name: str, default: str = "") -> str:
        """Return a header value using case-insensitive lookup."""

        wanted = name.lower()

        for key, value in self.headers.items():
            if key.lower() == wanted:
                return value

        return default

    def full_url(self) -> str:
        """Return an absolute URL when the request target is relative."""

        if self.url.startswith(("http://", "https://")):
            return self.url

        if not self.host:
            return self.url

        return urljoin(f"https://{self.host}", self.url)
