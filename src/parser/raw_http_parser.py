"""Parser for raw HTTP requests.

Role:
    Convert a pasted HTTP request into the shared HttpRequest model.

Example input:
    POST /change-email HTTP/1.1
    Host: example.com
    Content-Type: application/x-www-form-urlencoded

    email=test@example.com
"""
