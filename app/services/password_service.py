from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64
import os

def generate_password(password: str) -> str:
    """Génère un hash pour le mot de passe utilisateur"""
    return generate_password_hash(password)

def check_password(stored_hash: str, password: str) -> bool:
    """Vérifie si le mot de passe correspond au hash stocké"""
    return check_password_hash(stored_hash, password)

def generate_random_password(length=16, include_uppercase=True, include_digits=True, include_special=True) -> str:
    """
    Génère un mot de passe aléatoire sécurisé
    
    Args:
        length: Longueur du mot de passe (défaut: 16)
        include_uppercase: Inclure des lettres majuscules (défaut: True)
        include_digits: Inclure des chiffres (défaut: True)
        include_special: Inclure des caractères spéciaux (défaut: True)
        
    Returns:
        Mot de passe aléatoire généré
    """
    # Définir les ensembles de caractères
    chars = string.ascii_lowercase
    if include_uppercase:
        chars += string.ascii_uppercase
    if include_digits:
        chars += string.digits
    if include_special:
        chars += string.punctuation
    
    # Générer le mot de passe en utilisant secrets pour une sécurité cryptographique
    secure_password = ''.join(secrets.choice(chars) for _ in range(length))
    
    return secure_password

def encrypt_password(password, key=None):
    """
    Chiffre un mot de passe avec AES-256
    
    Args:
        password: Mot de passe à chiffrer
        key: Clé de chiffrement (générée si non fournie)
        
    Returns:
        Tuple (mot de passe chiffré encodé en base64, IV encodé en base64, clé encodée en base64)
    """
    if key is None:
        # Générer une clé AES-256 (32 bytes)
        key = os.urandom(32)
    
    # Générer un vecteur d'initialisation (IV)
    iv = os.urandom(16)
    
    # Convertir le mot de passe en bytes s'il est une chaîne
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    # Appliquer un padding pour que la longueur soit un multiple de la taille de bloc
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(password) + padder.finalize()
    
    # Créer un chiffreur AES-256 en mode CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Chiffrer les données
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    # Encoder en base64 pour le stockage
    encoded_ciphertext = base64.b64encode(ciphertext).decode('utf-8')
    encoded_iv = base64.b64encode(iv).decode('utf-8')
    encoded_key = base64.b64encode(key).decode('utf-8')
    
    return encoded_ciphertext, encoded_iv, encoded_key

def decrypt_password(encoded_ciphertext, encoded_iv, encoded_key):
    """
    Déchiffre un mot de passe chiffré avec AES-256
    
    Args:
        encoded_ciphertext: Mot de passe chiffré encodé en base64
        encoded_iv: IV encodé en base64
        encoded_key: Clé encodée en base64
        
    Returns:
        Mot de passe déchiffré
    """
    ciphertext = base64.b64decode(encoded_ciphertext)
    iv = base64.b64decode(encoded_iv)
    key = base64.b64decode(encoded_key)
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    
    return data.decode('utf-8')
