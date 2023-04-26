from email_validator import validate_email

register_schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string", "maxLength": 20},
        "email": {"type": "string", "maxLength": 120},
        "password": {"type": "string", "maxLength": 100}
    },
    "required": ["username", "email", "password"]
}


login_schema = {
    "type": "object",
    "properties": {
        "email": {"type": "string", "maxLength": 120},
        "password": {"type": "string", "maxLength": 100}
    },
    "required": ["email", "password"]
}
