"""Output writer.

Role:
    Save generated PoC content to disk.

This module should handle output paths, filenames, and overwrite behavior.
"""

from pathlib import Path


DEFAULT_OUTPUT_PATH = Path("examples/generated_poc.html")


def write_output(content: str, output_path: str | Path = DEFAULT_OUTPUT_PATH) -> Path:
    """Write generated content to disk and return the saved path."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    return path
