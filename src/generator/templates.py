"""HTML templates used by the generator.

Role:
    Store reusable template strings for generated PoC files.

Keeping templates here makes html_generator.py easier to read.
"""

HTML_POC_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CSRF PoC</title>
</head>
<body>
  <p>For authorized security testing only.</p>
  <form action="{action}" method="{method}">
{fields}
    <button type="submit">Submit request</button>
  </form>
  <script>
    document.forms[0].submit();
  </script>
</body>
</html>
"""

HIDDEN_INPUT_TEMPLATE = '    <input type="hidden" name="{name}" value="{value}">'
