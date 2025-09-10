from cryptography.fernet import Fernet
import os

fernet = Fernet(os.getenv("KEY"))

def encrypt_data(data: str):
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(token: str):
    return fernet.decrypt(token.encode()).decode()