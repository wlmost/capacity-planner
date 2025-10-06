"""
Unit Tests für Crypto Service
"""
import pytest
from pathlib import Path
import tempfile
import shutil
from src.services.crypto_service import CryptoService


class TestCryptoService:
    """Tests für CryptoService"""
    
    @pytest.fixture
    def temp_key_dir(self):
        """Erstellt temporäres Verzeichnis für Keys"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def crypto_service(self, temp_key_dir):
        """Erstellt CryptoService-Instanz mit temp Keys"""
        service = CryptoService(key_directory=temp_key_dir)
        service.initialize_keys()
        return service
    
    def test_initialize_keys_creates_key_files(self, temp_key_dir):
        """Test: initialize_keys sollte Key-Dateien erstellen"""
        service = CryptoService(key_directory=temp_key_dir)
        service.initialize_keys()
        
        assert (temp_key_dir / "private.pem").exists()
        assert (temp_key_dir / "public.pem").exists()
    
    def test_initialize_keys_loads_existing_keys(self, temp_key_dir):
        """Test: initialize_keys sollte existierende Keys laden"""
        # Erste Initialisierung
        service1 = CryptoService(key_directory=temp_key_dir)
        service1.initialize_keys()
        key1 = service1.private_key.export_key()
        
        # Zweite Initialisierung (sollte gleichen Key laden)
        service2 = CryptoService(key_directory=temp_key_dir)
        service2.initialize_keys()
        key2 = service2.private_key.export_key()
        
        assert key1 == key2
    
    def test_encrypt_decrypt_roundtrip(self, crypto_service):
        """Test: Verschlüsselung und Entschlüsselung sollten Original wiederherstellen"""
        plaintext = "Geheime Daten 🔒"
        
        encrypted = crypto_service.encrypt(plaintext)
        decrypted = crypto_service.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_encrypt_produces_different_ciphertexts(self, crypto_service):
        """Test: Gleicher Klartext sollte verschiedene Ciphertexts ergeben (wegen AES-Key)"""
        plaintext = "Test"
        
        encrypted1 = crypto_service.encrypt(plaintext)
        encrypted2 = crypto_service.encrypt(plaintext)
        
        assert encrypted1 != encrypted2
    
    def test_encrypt_without_keys_raises_error(self, temp_key_dir):
        """Test: encrypt ohne initialisierte Keys sollte RuntimeError werfen"""
        service = CryptoService(key_directory=temp_key_dir)
        
        with pytest.raises(RuntimeError, match="Keys nicht initialisiert"):
            service.encrypt("Test")
    
    def test_decrypt_without_keys_raises_error(self, temp_key_dir):
        """Test: decrypt ohne initialisierte Keys sollte RuntimeError werfen"""
        service = CryptoService(key_directory=temp_key_dir)
        
        with pytest.raises(RuntimeError, match="Keys nicht initialisiert"):
            service.decrypt("dummy")
    
    def test_encrypt_long_text(self, crypto_service):
        """Test: Verschlüsselung von längeren Texten"""
        plaintext = "Lorem ipsum dolor sit amet " * 100
        
        encrypted = crypto_service.encrypt(plaintext)
        decrypted = crypto_service.decrypt(encrypted)
        
        assert decrypted == plaintext
    
    def test_encrypt_special_characters(self, crypto_service):
        """Test: Verschlüsselung mit Sonderzeichen"""
        plaintext = "Umlaute: äöü ÄÖÜ ß, Emoji: 🎉🔐, Symbole: @#$%^&*()"
        
        encrypted = crypto_service.encrypt(plaintext)
        decrypted = crypto_service.decrypt(encrypted)
        
        assert decrypted == plaintext
