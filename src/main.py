"""Command-line entry point for the CSRF PoC generator.

This file will eventually handle user input, call the parser, run analysis,
generate the HTML PoC, and write the result to disk.
"""

import argparse
from pathlib import Path

from src.core.csrf_analyzer import analyze_request
from src.generator.html_generator import generate_html_poc
from src.output.writer import DEFAULT_OUTPUT_PATH, write_output
from src.parser.raw_http_parser import RawHttpParseError, parse_raw_http


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""

    parser = argparse.ArgumentParser(
        description="Generate an HTML CSRF PoC from a raw HTTP request."
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to a file containing a raw HTTP request.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Path where the generated HTML PoC should be saved.",
    )

    return parser


def run(input_path: str | Path, output_path: str | Path) -> Path:
    """Run the request parsing, analysis, generation, and writing pipeline."""

    raw_request = Path(input_path).read_text(encoding="utf-8")
    request = parse_raw_http(raw_request)
    analysis = analyze_request(request)

    for warning in analysis.warnings:
        print(f"Warning: {warning}")

    html = generate_html_poc(request)
    saved_path = write_output(html, output_path)

    print(f"Generated CSRF PoC: {saved_path}")

    return saved_path


def main() -> None:
    """Parse CLI arguments and run the generator."""

    parser = build_parser()
    args = parser.parse_args()

    try:
        run(args.input, args.output)
    except (OSError, RawHttpParseError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
