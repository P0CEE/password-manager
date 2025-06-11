from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os

def generate_password(password: str) -> str:
    """Génère un hash pour le mot de passe utilisateur"""
    return generate_password_hash(password)

def check_password(stored_hash: str, password: str) -> bool:
    """Vérifie si le mot de passe correspond au hash stocké"""
    return check_password_hash(stored_hash, password)

def derive_user_key(user_id: int, user_salt: str) -> bytes:
    """Dérive une clé unique pour chaque utilisateur"""
    key_material = f"user_{user_id}_{user_salt}".encode()
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'password_manager_salt',
        iterations=100000,
    )
    return kdf.derive(key_material)

def encrypt_password(password, user_id: int, user_salt: str):
    """Chiffre un mot de passe avec la clé de l'utilisateur"""
    user_key = derive_user_key(user_id, user_salt)
    iv = os.urandom(16)
    
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(password) + padder.finalize()
    
    cipher = Cipher(algorithms.AES(user_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    encoded_ciphertext = base64.b64encode(ciphertext).decode('utf-8')
    encoded_iv = base64.b64encode(iv).decode('utf-8')
    
    return encoded_ciphertext, encoded_iv

def decrypt_password(encoded_ciphertext, encoded_iv, user_id: int, user_salt: str):
    """Déchiffre un mot de passe avec la clé de l'utilisateur"""
    user_key = derive_user_key(user_id, user_salt)
    
    ciphertext = base64.b64decode(encoded_ciphertext)
    iv = base64.b64decode(encoded_iv)
    
    cipher = Cipher(algorithms.AES(user_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    
    return data.decode('utf-8')

def generate_random_password(length=16, include_uppercase=True, include_digits=True, include_special=True) -> str:
    chars = string.ascii_lowercase
    if include_uppercase:
        chars += string.ascii_uppercase
    if include_digits:
        chars += string.digits
    if include_special:
        chars += string.punctuation
    
    secure_password = ''.join(secrets.choice(chars) for _ in range(length))
    return secure_password