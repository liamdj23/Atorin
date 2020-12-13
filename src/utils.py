def bool_to_state(value: bool):
    if value:
        return "✅ Włączone"
    else:
        return "❌ Wyłączone"


def state_to_bool(value: str):
    if value.lower() == "on":
        return True
    elif value.lower() == "off":
        return False
    else:
        return None
