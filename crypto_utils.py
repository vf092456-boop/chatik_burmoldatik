import base64

# Простой XOR-ключ (для демонстрации, в реальности используйте сильную криптографию)
KEY = b"my_secret_key_2025"

def encrypt(text: str) -> str:
    """Шифрует текст XOR с ключом и кодирует в base64"""
    if isinstance(text, str):
        text = text.encode('utf-8')
    # XOR с повторяющимся ключом
    encrypted = bytes([text[i] ^ KEY[i % len(KEY)] for i in range(len(text))])
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt(encrypted_b64: str) -> str:
    """Декодирует base64 и расшифровывает XOR"""
    encrypted = base64.b64decode(encrypted_b64)
    decrypted = bytes([encrypted[i] ^ KEY[i % len(KEY)] for i in range(len(encrypted))])
    return decrypted.decode('utf-8', errors='replace')