import base64

KEY = b"my_secret_key_2025"

def encrypt(text: str) -> str:
    if isinstance(text, str):
        text = text.encode('utf-8')
    encrypted = bytes([text[i] ^ KEY[i % len(KEY)] for i in range(len(text))])
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt(encrypted_b64: str) -> str:
    try:
        encrypted = base64.b64decode(encrypted_b64)
        decrypted = bytes([encrypted[i] ^ KEY[i % len(KEY)] for i in range(len(encrypted))])
        return decrypted.decode('utf-8', errors='replace')
    except Exception:
        return "[ошибка расшифровки]"
