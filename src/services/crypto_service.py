"""
Crypto Service
Verschlüsselung sensibler Daten mit RSA/AES
"""
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
import base64
from typing import Tuple, Optional
from pathlib import Path


class CryptoService:
    """
    Verschlüsselungsservice für sensible Daten
    
    Strategie:
    - RSA für Key Exchange (asymmetrisch)
    - AES für Daten-Verschlüsselung (symmetrisch, schneller)
    
    Workflow:
    1. RSA-Keypair generieren/laden
    2. AES-Key für jede Verschlüsselung generieren
    3. AES-Key mit RSA-Public-Key verschlüsseln
    4. Daten mit AES verschlüsseln
    5. Speichern: encrypted_aes_key + encrypted_data
    
    Beispiel:
        >>> crypto = CryptoService()
        >>> crypto.initialize_keys()
        >>> encrypted = crypto.encrypt("Geheime Daten")
        >>> decrypted = crypto.decrypt(encrypted)
    """
    
    RSA_KEY_SIZE = 2048
    AES_KEY_SIZE = 32  # 256 bit
    
    def __init__(self, key_directory: Optional[Path] = None):
        """
        Initialisiert den Crypto Service
        
        Args:
            key_directory: Verzeichnis für Schlüsselspeicherung
        """
        self.key_directory = key_directory or Path.home() / ".capacity_planner" / "keys"
        self.key_directory.mkdir(parents=True, exist_ok=True)
        
        self.private_key: Optional[RSA.RsaKey] = None
        self.public_key: Optional[RSA.RsaKey] = None
    
    def initialize_keys(self, force_new: bool = False) -> None:
        """
        Generiert oder lädt RSA-Keys
        
        Args:
            force_new: Erzwingt neue Key-Generierung
        """
        private_key_path = self.key_directory / "private.pem"
        public_key_path = self.key_directory / "public.pem"
        
        if not force_new and private_key_path.exists() and public_key_path.exists():
            self._load_keys(private_key_path, public_key_path)
        else:
            self._generate_keys(private_key_path, public_key_path)
    
    def _generate_keys(self, private_path: Path, public_path: Path) -> None:
        """Generiert neues RSA-Keypair"""
        key = RSA.generate(self.RSA_KEY_SIZE)
        self.private_key = key
        self.public_key = key.publickey()
        
        # Speichern
        with open(private_path, 'wb') as f:
            f.write(key.export_key())
        
        with open(public_path, 'wb') as f:
            f.write(self.public_key.export_key())
    
    def _load_keys(self, private_path: Path, public_path: Path) -> None:
        """Lädt existierendes RSA-Keypair"""
        with open(private_path, 'rb') as f:
            self.private_key = RSA.import_key(f.read())
        
        with open(public_path, 'rb') as f:
            self.public_key = RSA.import_key(f.read())
    
    def encrypt(self, plaintext: str) -> str:
        """
        Verschlüsselt Text mit AES, AES-Key mit RSA
        
        Args:
            plaintext: Zu verschlüsselnder Text
            
        Returns:
            Base64-kodierter String: encrypted_aes_key + nonce + tag + ciphertext
        """
        if not self.public_key:
            raise RuntimeError("Keys nicht initialisiert. Rufe initialize_keys() auf.")
        
        # AES-Key generieren
        aes_key = get_random_bytes(self.AES_KEY_SIZE)
        
        # AES-Key mit RSA verschlüsseln
        rsa_cipher = PKCS1_OAEP.new(self.public_key)
        encrypted_aes_key = rsa_cipher.encrypt(aes_key)
        
        # Daten mit AES verschlüsseln (GCM Mode für Authenticity)
        aes_cipher = AES.new(aes_key, AES.MODE_GCM)
        ciphertext, tag = aes_cipher.encrypt_and_digest(plaintext.encode('utf-8'))
        
        # Alles zusammenfügen und Base64-kodieren
        combined = encrypted_aes_key + aes_cipher.nonce + tag + ciphertext
        return base64.b64encode(combined).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Entschlüsselt verschlüsselte Daten
        
        Args:
            encrypted_data: Base64-kodierter verschlüsselter String
            
        Returns:
            Entschlüsselter Klartext
        """
        if not self.private_key:
            raise RuntimeError("Keys nicht initialisiert. Rufe initialize_keys() auf.")
        
        # Base64 dekodieren
        combined = base64.b64decode(encrypted_data)
        
        # Komponenten extrahieren
        rsa_key_size_bytes = self.RSA_KEY_SIZE // 8
        encrypted_aes_key = combined[:rsa_key_size_bytes]
        nonce = combined[rsa_key_size_bytes:rsa_key_size_bytes + 16]
        tag = combined[rsa_key_size_bytes + 16:rsa_key_size_bytes + 32]
        ciphertext = combined[rsa_key_size_bytes + 32:]
        
        # AES-Key mit RSA entschlüsseln
        rsa_cipher = PKCS1_OAEP.new(self.private_key)
        aes_key = rsa_cipher.decrypt(encrypted_aes_key)
        
        # Daten mit AES entschlüsseln
        aes_cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        plaintext = aes_cipher.decrypt_and_verify(ciphertext, tag)
        
        return plaintext.decode('utf-8')
