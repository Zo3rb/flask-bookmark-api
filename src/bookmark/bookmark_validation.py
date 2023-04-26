create_bookmark_schema = {
    "type": "object",
    "properties": {
        "url": {"type": "string", "format": "uri"},
        "body": {"type": "string"}
    },
    "required": ["url", "body"]
}
