import re


def urljoin(*parts: str):
    """Прокаченая версия urljoin."""

    if len(parts) == 0:
        return ""

    parsed_parts = [
        re.sub(r"^\/+|\/+$", "", part, 0, re.MULTILINE) for part in parts if part
    ]
    parsed_parts = [part for part in parsed_parts if len(part) > 0]

    url = "/".join(parsed_parts)

    if parts[0] == "/":
        url = "/" + url

    return url
