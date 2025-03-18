from werkzeug.security import generate_password_hash, check_password_hash

def generate_password(password: str) -> str:
    return generate_password_hash(password)

def check_password(stored_hash: str, password: str) -> bool:
    return check_password_hash(stored_hash, password)
