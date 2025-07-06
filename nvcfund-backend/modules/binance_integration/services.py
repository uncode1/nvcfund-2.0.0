"""
Binance Integration Services
OAuth 2.0 authentication and API services for Binance integration
"""

import os
import logging
import secrets
import hashlib
import base64
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs, urlparse
import json

logger = logging.getLogger(__name__)

class BinanceOAuthService:
    """
    Binance OAuth 2.0 authentication service
    Handles authorization flow, token management, and secure API access
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Binance OAuth endpoints
        self.auth_base_url = "https://accounts.binance.com/en/oauth/authorize"
        self.token_url = "https://accounts.binance.com/oauth/token"
        self.api_base_url = "https://www.binanceapis.com/oauth-api/v1"
        
        # OAuth configuration from environment
        self.client_id = os.environ.get('BINANCE_CLIENT_ID')
        self.client_secret = os.environ.get('BINANCE_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('BINANCE_REDIRECT_URI', 'https://localhost:5000/binance/callback')
        
        # Supported scopes
        self.available_scopes = [
            'user:openId',
            'user:email',
            'create:apikey',
            'read:account',
            'trade:spot',
            'trade:futures'
        ]
        
    def generate_authorization_url(self, scopes: List[str], state: Optional[str] = None) -> Dict[str, str]:
        """
        Generate OAuth authorization URL with PKCE or standard flow
        
        Args:
            scopes: List of requested permission scopes
            state: CSRF protection token
            
        Returns:
            Dictionary containing authorization URL and verification data
        """
        try:
            # Generate CSRF state token if not provided
            if not state:
                state = secrets.token_urlsafe(32)
            
            # Generate PKCE code verifier and challenge for browser/mobile apps
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            
            # Validate requested scopes
            invalid_scopes = [scope for scope in scopes if scope not in self.available_scopes]
            if invalid_scopes:
                raise ValueError(f"Invalid scopes requested: {invalid_scopes}")
            
            # Build authorization parameters
            auth_params = {
                'response_type': 'code',
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'state': state,
                'scope': ','.join(scopes),
                'code_challenge': code_challenge,
                'code_challenge_method': 'S256'
            }
            
            authorization_url = f"{self.auth_base_url}?{urlencode(auth_params)}"
            
            self.logger.info(f"Generated Binance OAuth authorization URL for scopes: {scopes}")
            
            return {
                'authorization_url': authorization_url,
                'state': state,
                'code_verifier': code_verifier,
                'scopes_requested': scopes
            }
            
        except Exception as e:
            self.logger.error(f"Error generating authorization URL: {e}")
            raise
    
    def exchange_code_for_tokens(self, authorization_code: str, code_verifier: Optional[str] = None) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            authorization_code: Code received from OAuth callback
            code_verifier: PKCE code verifier (for PKCE flow)
            
        Returns:
            Token response with access_token, refresh_token, and metadata
        """
        try:
            if not self.client_id or not self.client_secret:
                raise ValueError("Binance client credentials not configured")
            
            # Prepare token exchange request
            token_data = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri
            }
            
            # Add PKCE code verifier if provided
            if code_verifier:
                token_data['code_verifier'] = code_verifier
            
            # Make token exchange request
            response = requests.post(
                self.token_url,
                data=token_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                token_response = response.json()
                
                # Add token metadata
                token_response['created_at'] = datetime.utcnow().isoformat()
                token_response['expires_at'] = (
                    datetime.utcnow() + timedelta(seconds=token_response.get('expires_in', 3600))
                ).isoformat()
                
                self.logger.info("Successfully exchanged authorization code for tokens")
                return token_response
            else:
                error_msg = f"Token exchange failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Error exchanging code for tokens: {e}")
            raise
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New token response
        """
        try:
            refresh_data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(
                self.token_url,
                data=refresh_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                token_response = response.json()
                
                # Add token metadata
                token_response['created_at'] = datetime.utcnow().isoformat()
                token_response['expires_at'] = (
                    datetime.utcnow() + timedelta(seconds=token_response.get('expires_in', 3600))
                ).isoformat()
                
                self.logger.info("Successfully refreshed access token")
                return token_response
            else:
                error_msg = f"Token refresh failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Error refreshing access token: {e}")
            raise
    
    def revoke_access_token(self, access_token: str) -> bool:
        """
        Revoke access token to invalidate session
        
        Args:
            access_token: Valid access token to revoke
            
        Returns:
            True if revocation successful
        """
        try:
            response = requests.post(
                f"{self.api_base_url}/revoke-token",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                success = result.get('success', False) and result.get('data', False)
                
                if success:
                    self.logger.info("Successfully revoked access token")
                    return True
                else:
                    self.logger.warning(f"Token revocation returned unsuccessful: {result}")
                    return False
            else:
                self.logger.error(f"Token revocation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error revoking access token: {e}")
            return False
    
    def _generate_code_verifier(self) -> str:
        """Generate PKCE code verifier"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    def _generate_code_challenge(self, code_verifier: str) -> str:
        """Generate PKCE code challenge from verifier"""
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')


class BinanceAPIService:
    """
    Binance API service for authenticated requests
    Handles user data retrieval and account operations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.api_base_url = "https://www.binanceapis.com/oauth-api/v1"
        
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information using OAuth access token
        
        Args:
            access_token: Valid Binance OAuth access token
            
        Returns:
            User information from Binance API
        """
        try:
            response = requests.get(
                f"{self.api_base_url}/user-info",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success', False):
                    user_data = result.get('data', {})
                    self.logger.info(f"Successfully retrieved user info for user: {user_data.get('userId', 'unknown')}")
                    return {
                        'status': 'success',
                        'user_data': user_data,
                        'retrieved_at': datetime.utcnow().isoformat()
                    }
                else:
                    error_msg = f"API returned unsuccessful: {result.get('message', 'Unknown error')}"
                    self.logger.error(error_msg)
                    return {
                        'status': 'error',
                        'error': error_msg,
                        'code': result.get('code', 'unknown')
                    }
            else:
                error_msg = f"API request failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {
                    'status': 'error',
                    'error': error_msg,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            self.logger.error(f"Error getting user info: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def validate_token(self, access_token: str) -> Dict[str, Any]:
        """
        Validate access token by making a test API call
        
        Args:
            access_token: Access token to validate
            
        Returns:
            Validation result with token status
        """
        try:
            user_info = self.get_user_info(access_token)
            
            if user_info['status'] == 'success':
                return {
                    'valid': True,
                    'user_id': user_info['user_data'].get('userId'),
                    'email': user_info['user_data'].get('email'),
                    'validated_at': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'valid': False,
                    'error': user_info.get('error', 'Token validation failed'),
                    'validated_at': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error validating token: {e}")
            return {
                'valid': False,
                'error': str(e),
                'validated_at': datetime.utcnow().isoformat()
            }


class BinanceIntegrationService:
    """
    Main Binance integration service
    Combines OAuth and API services for complete integration
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.oauth_service = BinanceOAuthService()
        self.api_service = BinanceAPIService()
        
    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get current integration status and configuration
        
        Returns:
            Integration status information
        """
        try:
            has_credentials = bool(
                os.environ.get('BINANCE_CLIENT_ID') and 
                os.environ.get('BINANCE_CLIENT_SECRET')
            )
            
            return {
                'status': 'configured' if has_credentials else 'not_configured',
                'has_credentials': has_credentials,
                'redirect_uri': self.oauth_service.redirect_uri,
                'available_scopes': self.oauth_service.available_scopes,
                'api_endpoints': [
                    'user-info',
                    'revoke-token'
                ],
                'oauth_flows_supported': [
                    'authorization_code',
                    'pkce'
                ],
                'last_checked': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting integration status: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'last_checked': datetime.utcnow().isoformat()
            }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get dashboard data for Binance integration overview
        
        Returns:
            Dashboard data with integration metrics
        """
        try:
            integration_status = self.get_integration_status()
            
            return {
                'integration_status': integration_status,
                'oauth_endpoints': {
                    'authorization': self.oauth_service.auth_base_url,
                    'token': self.oauth_service.token_url,
                    'api_base': self.oauth_service.api_base_url
                },
                'security_features': [
                    'OAuth 2.0 Authorization Code Flow',
                    'PKCE (Proof Key for Code Exchange)',
                    'CSRF Protection with State Parameter',
                    'Secure Token Storage',
                    'Token Refresh and Revocation'
                ],
                'supported_operations': [
                    'User Authentication',
                    'Account Information Retrieval',
                    'Token Management',
                    'Secure API Access'
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            return {
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }