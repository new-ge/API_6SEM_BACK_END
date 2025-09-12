from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
import glob

dotenv_path = glob.glob(os.path.join(os.path.dirname(__file__), "*.env"))
load_dotenv(dotenv_path[0])

fernet = Fernet(os.getenv("KEY"))

def encrypt_data(data: str):
    if not isinstance(data, str):
        data = str(data)
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(token: str):
    return fernet.decrypt(token.encode()).decode()