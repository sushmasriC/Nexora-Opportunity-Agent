"""
Descope token verification service for backend API.
Handles verification of Descope session tokens from frontend.
"""

import requests
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from ..config import settings

logger = logging.getLogger(__name__)


class DescopeTokenVerification:
    """Service for verifying Descope session tokens."""
    
    def __init__(self):
        """Initialize Descope verification service."""
        self.project_id = settings.descope_project_id
        self.api_key = settings.descope_api_key
        self.base_url = f"https://api.descope.com/v1/projects/{self.project_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def is_configured(self) -> bool:
        """Check if Descope is properly configured."""
        return bool(self.project_id and self.api_key)
    
    def verify_session_token(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a Descope session token and return user information.
        
        Args:
            session_token: Descope session token from frontend
            
        Returns:
            User information if token is valid, None otherwise
        """
        if not self.is_configured():
            logger.warning("Descope not configured, using mock verification")
            return self._mock_verify_token(session_token)
        
        try:
            # Verify token with Descope
            response = requests.post(
                f"{self.base_url}/auth/validate",
                headers=self.headers,
                json={"token": session_token},
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                logger.info(f"Token verified successfully for user: {token_data.get('sub', 'unknown')}")
                return token_data
            else:
                logger.warning(f"Token verification failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error verifying Descope token: {e}")
            return None
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information from Descope.
        
        Args:
            user_id: Descope user ID
            
        Returns:
            User information if found, None otherwise
        """
        if not self.is_configured():
            logger.warning("Descope not configured, using mock user info")
            return self._mock_get_user_info(user_id)
        
        try:
            response = requests.get(
                f"{self.base_url}/users/{user_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                user_info = response.json()
                return user_info
            else:
                logger.warning(f"Failed to get user info for {user_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user info for {user_id}: {e}")
            return None
    
    def _mock_verify_token(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Mock token verification for development/testing."""
        # For development, accept any non-empty token
        if session_token and len(session_token) > 10:
            return {
                "sub": "mock_user_123",
                "email": "test@example.com",
                "user_id": "mock_user_123",
                "iat": int(datetime.now().timestamp()),
                "exp": int(datetime.now().timestamp()) + 3600
            }
        return None
    
    def _mock_get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Mock user info for development/testing."""
        return {
            "id": user_id,
            "email": f"user_{user_id}@example.com",
            "name": f"User {user_id}",
            "created_at": datetime.now().isoformat()
        }


# Global instance
descope_verifier = DescopeTokenVerification()

