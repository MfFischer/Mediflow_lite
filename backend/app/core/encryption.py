"""
Data encryption utilities for HIPAA/GDPR compliance.
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import json
from typing import Optional

from .config import settings


class DataEncryption:
    """
    Handles encryption and decryption of sensitive data.

    Uses Fernet (symmetric encryption) for field-level encryption.
    """

    def __init__(self):
        """Initialize encryption with key derived from secret."""
        # Derive encryption key from secret key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'mediflow_salt_change_in_production',  # Should be unique per installation
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(settings.secret_key.encode()))
        self.cipher = Fernet(key)

        # AES key for full-record encryption
        self.aes_key = kdf.derive(settings.secret_key.encode())[:32]

    def encrypt(self, data: str) -> str:
        """
        Encrypt a string.

        Args:
            data: Plain text string to encrypt

        Returns:
            Encrypted string (base64 encoded)
        """
        if not data:
            return data

        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode()

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt a string.

        Args:
            encrypted_data: Encrypted string (base64 encoded)

        Returns:
            Decrypted plain text string
        """
        if not encrypted_data:
            return encrypted_data

        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            # Log error but don't expose details
            raise ValueError("Failed to decrypt data") from e

    def encrypt_dict(self, data: dict, fields: list[str]) -> dict:
        """
        Encrypt specific fields in a dictionary.

        Args:
            data: Dictionary containing data
            fields: List of field names to encrypt

        Returns:
            Dictionary with encrypted fields
        """
        encrypted_data = data.copy()
        for field in fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        return encrypted_data

    def decrypt_dict(self, data: dict, fields: list[str]) -> dict:
        """
        Decrypt specific fields in a dictionary.

        Args:
            data: Dictionary containing encrypted data
            fields: List of field names to decrypt

        Returns:
            Dictionary with decrypted fields
        """
        decrypted_data = data.copy()
        for field in fields:
            if field in decrypted_data and decrypted_data[field]:
                decrypted_data[field] = self.decrypt(decrypted_data[field])
        return decrypted_data

    def encrypt_aes(self, data: bytes) -> bytes:
        """
        Encrypt data using AES-256-CBC for full-record encryption.

        Args:
            data: Bytes to encrypt

        Returns:
            IV + encrypted bytes
        """
        # Generate random IV
        iv = os.urandom(16)

        # Pad data to AES block size
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()

        # Encrypt
        cipher = Cipher(
            algorithms.AES(self.aes_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()

        # Return IV + encrypted data
        return iv + encrypted

    def decrypt_aes(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data using AES-256-CBC.

        Args:
            encrypted_data: IV + encrypted bytes

        Returns:
            Decrypted bytes
        """
        # Extract IV and encrypted data
        iv = encrypted_data[:16]
        encrypted = encrypted_data[16:]

        # Decrypt
        cipher = Cipher(
            algorithms.AES(self.aes_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted) + decryptor.finalize()

        # Unpad
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()

        return data

    def encrypt_record(self, record: dict) -> str:
        """
        Encrypt an entire record (full-record encryption).

        Args:
            record: Dictionary to encrypt

        Returns:
            Base64-encoded encrypted record
        """
        json_data = json.dumps(record)
        encrypted_bytes = self.encrypt_aes(json_data.encode())
        return base64.b64encode(encrypted_bytes).decode()

    def decrypt_record(self, encrypted_record: str) -> dict:
        """
        Decrypt an entire record.

        Args:
            encrypted_record: Base64-encoded encrypted record

        Returns:
            Decrypted dictionary
        """
        encrypted_bytes = base64.b64decode(encrypted_record.encode())
        decrypted_bytes = self.decrypt_aes(encrypted_bytes)
        return json.loads(decrypted_bytes.decode())

    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Encrypt a file.

        Args:
            file_path: Path to file to encrypt
            output_path: Optional output path

        Returns:
            Path to encrypted file
        """
        with open(file_path, 'rb') as f:
            data = f.read()

        encrypted = self.encrypt_aes(data)

        output = output_path or f"{file_path}.encrypted"
        with open(output, 'wb') as f:
            f.write(encrypted)

        return output

    def decrypt_file(self, encrypted_path: str, output_path: Optional[str] = None) -> str:
        """
        Decrypt a file.

        Args:
            encrypted_path: Path to encrypted file
            output_path: Optional output path

        Returns:
            Path to decrypted file
        """
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()

        decrypted = self.decrypt_aes(encrypted_data)

        output = output_path or encrypted_path.replace('.encrypted', '')
        with open(output, 'wb') as f:
            f.write(decrypted)

        return output


# Global encryption instance
encryption = DataEncryption()


def hash_data(data: str) -> str:
    """
    Create a one-way hash of data (for anonymization).

    Args:
        data: Data to hash

    Returns:
        SHA256 hash of the data
    """
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(data.encode())
    return base64.b64encode(digest.finalize()).decode()





# Sensitive fields that should always be encrypted
SENSITIVE_FIELDS = {
    'patients': ['ssn', 'insurance_number', 'medical_history'],
    'prescriptions': ['diagnosis', 'notes'],
    'lab_results': ['notes', 'doctor_comments'],
    'appointments': ['notes']
}


def get_sensitive_fields(model_name: str) -> list:
    """
    Get list of sensitive fields for a model.

    Args:
        model_name: Name of the model

    Returns:
        List of sensitive field names
    """
    return SENSITIVE_FIELDS.get(model_name, [])