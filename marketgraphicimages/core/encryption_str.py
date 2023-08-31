from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_value(value: str) -> str:
    """Hashing value using multiple algorithms."""
    return pwd_context.hash(value)


def verify_value(value: str, hash_value: str) -> bool:
    """Verifying value using multiple algorithms."""
    return pwd_context.verify(value, hash_value)
