def get_content_type(file_name: str):
    extension = file_name.split(".")[-1].lower()
    content_types = {
        "js": "application/javascript",
        "html": "text/html",
        "txt": "text/plain",
        "json": "application/json",
        "ico": "image/x-icon",
        "svg": "image/svg+xml",
        "css": "text/css",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "map": "binary/octet-stream",
    }
    return content_types.get(extension, "application/octet-stream")
