"""
API Key Management System for NVC Banking Platform
Secure storage and retrieval of external API credentials
"""

import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class APIKeyStore:
    """File-based secure storage for external API keys"""
    
    def __init__(self, service_name, encrypted_api_key=None, encrypted_secret_key=None, 
                 key_alias=None, is_active=True, created_at=None, updated_at=None, 
                 last_used=None, usage_count=0):
        self.service_name = service_name
        self.encrypted_api_key = encrypted_api_key
        self.encrypted_secret_key = encrypted_secret_key
        self.key_alias = key_alias
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.last_used = last_used
        self.usage_count = usage_count
    
    def to_dict(self):
        return {
            'service_name': self.service_name,
            'encrypted_api_key': self.encrypted_api_key,
            'encrypted_secret_key': self.encrypted_secret_key,
            'key_alias': self.key_alias,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_count': self.usage_count
        }
    
    @classmethod
    def from_dict(cls, data):
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        last_used = datetime.fromisoformat(data['last_used']) if data.get('last_used') else None
        
        return cls(
            service_name=data['service_name'],
            encrypted_api_key=data.get('encrypted_api_key'),
            encrypted_secret_key=data.get('encrypted_secret_key'),
            key_alias=data.get('key_alias'),
            is_active=data.get('is_active', True),
            created_at=created_at,
            updated_at=updated_at,
            last_used=last_used,
            usage_count=data.get('usage_count', 0)
        )
    
    def __repr__(self):
        return f'<APIKeyStore {self.service_name}>'

class APIKeyManager:
    """Secure API Key Management System"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self):
        """Generate or retrieve encryption key from environment"""
        # Use a combination of DATABASE_URL and fixed salt for deterministic key generation
        password = (os.environ.get('DATABASE_URL', 'default_key') + 'nvc_api_salt').encode()
        salt = b'nvc_banking_platform_salt_2025'
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def store_api_key(self, service_name: str, api_key: str = None, secret_key: str = None, alias: str = None):
        """Store encrypted API credentials"""
        try:
            # Check if service already exists
            existing = APIKeyStore.query.filter_by(service_name=service_name).first()
            
            if existing:
                # Update existing record
                if api_key:
                    existing.encrypted_api_key = self.cipher_suite.encrypt(api_key.encode()).decode()
                if secret_key:
                    existing.encrypted_secret_key = self.cipher_suite.encrypt(secret_key.encode()).decode()
                if alias:
                    existing.key_alias = alias
                existing.updated_at = datetime.utcnow()
                record = existing
            else:
                # Create new record
                encrypted_api = self.cipher_suite.encrypt(api_key.encode()).decode() if api_key else None
                encrypted_secret = self.cipher_suite.encrypt(secret_key.encode()).decode() if secret_key else None
                
                record = APIKeyStore(
                    service_name=service_name,
                    encrypted_api_key=encrypted_api,
                    encrypted_secret_key=encrypted_secret,
                    key_alias=alias
                )
                db.session.add(record)
            
            db.session.commit()
            logger.info(f"API key stored successfully for service: {service_name}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error storing API key for {service_name}: {str(e)}")
            return False
    
    def get_api_key(self, service_name: str):
        """Retrieve and decrypt API credentials"""
        try:
            record = APIKeyStore.query.filter_by(service_name=service_name, is_active=True).first()
            
            if not record:
                return None
            
            # Update usage statistics
            record.last_used = datetime.utcnow()
            record.usage_count += 1
            db.session.commit()
            
            # Decrypt credentials
            api_key = None
            secret_key = None
            
            if record.encrypted_api_key:
                api_key = self.cipher_suite.decrypt(record.encrypted_api_key.encode()).decode()
            
            if record.encrypted_secret_key:
                secret_key = self.cipher_suite.decrypt(record.encrypted_secret_key.encode()).decode()
            
            return {
                'api_key': api_key,
                'secret_key': secret_key,
                'alias': record.key_alias,
                'last_used': record.last_used,
                'usage_count': record.usage_count
            }
            
        except Exception as e:
            logger.error(f"Error retrieving API key for {service_name}: {str(e)}")
            return None
    
    def list_services(self):
        """List all stored API services"""
        try:
            records = APIKeyStore.query.filter_by(is_active=True).all()
            return [{
                'service_name': record.service_name,
                'alias': record.key_alias,
                'has_api_key': bool(record.encrypted_api_key),
                'has_secret_key': bool(record.encrypted_secret_key),
                'created_at': record.created_at,
                'last_used': record.last_used,
                'usage_count': record.usage_count
            } for record in records]
        except Exception as e:
            logger.error(f"Error listing API services: {str(e)}")
            return []
    
    def deactivate_service(self, service_name: str):
        """Deactivate API key without deleting"""
        try:
            record = APIKeyStore.query.filter_by(service_name=service_name).first()
            if record:
                record.is_active = False
                record.updated_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"API key deactivated for service: {service_name}")
                return True
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deactivating API key for {service_name}: {str(e)}")
            return False
    
    def delete_service(self, service_name: str):
        """Permanently delete API key"""
        try:
            record = APIKeyStore.query.filter_by(service_name=service_name).first()
            if record:
                db.session.delete(record)
                db.session.commit()
                logger.info(f"API key deleted for service: {service_name}")
                return True
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting API key for {service_name}: {str(e)}")
            return False

# Global instance
api_key_manager = APIKeyManager()

# Convenience functions for Binance specifically
def store_binance_credentials(api_key: str, secret_key: str, alias: str = "Production"):
    """Store Binance API credentials"""
    return api_key_manager.store_api_key('binance', api_key, secret_key, alias)

def get_binance_credentials():
    """Get Binance API credentials"""
    return api_key_manager.get_api_key('binance')

def store_polygonscan_key(api_key: str, alias: str = "Production"):
    """Store Polygonscan API key"""
    return api_key_manager.store_api_key('polygonscan', api_key=api_key, alias=alias)

def get_polygonscan_key():
    """Get Polygonscan API key"""
    creds = api_key_manager.get_api_key('polygonscan')
    return creds['api_key'] if creds else None

def store_etherscan_key(api_key: str, alias: str = "Production"):
    """Store Etherscan API key"""
    return api_key_manager.store_api_key('etherscan', api_key=api_key, alias=alias)

def get_etherscan_key():
    """Get Etherscan API key"""
    creds = api_key_manager.get_api_key('etherscan')
    return creds['api_key'] if creds else None