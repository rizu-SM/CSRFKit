"""CSRF compatibility analyzer.

Role:
    Inspect a normalized HttpRequest and decide whether it can be represented
    as a browser-submitable CSRF PoC.

This module should also produce warnings for requests that may not work well,
such as JSON APIs, bearer tokens, or required custom headers.
"""
