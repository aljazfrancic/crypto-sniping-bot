import os
from cryptography.fernet import Fernet

def get_key():
    encrypted_key = os.getenv("PRIVATE_KEY")
    if encrypted_key and encrypted_key.startswith("encrypted:"):
        cipher = Fernet(os.getenv("ENCRYPTION_KEY"))
        return cipher.decrypt(encrypted_key[10:].encode()).decode()
    return encrypted_key

def encrypt_key(raw_key: str) -> str:
    if not os.getenv("ENCRYPTION_KEY"):
        key = Fernet.generate_key()
        print(f"[KEY] NEW ENCRYPTION KEY: {key.decode()}")
        print("Add this to your .env as ENCRYPTION_KEY")
        os.environ["ENCRYPTION_KEY"] = key.decode()
    cipher = Fernet(os.getenv("ENCRYPTION_KEY").encode())
    return "encrypted:" + cipher.encrypt(raw_key.encode()).decode()