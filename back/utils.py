def validate_required_fields(data, *fields):
    missing = [field for field in fields if not data.get(field)]
    if missing:
        return False, f"Faltan los siguientes campos: {', '.join(missing)}"
    return True, None