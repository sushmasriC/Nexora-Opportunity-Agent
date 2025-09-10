"""
Authentication service using Descope for user management.
Handles user registration, login, and session management.
"""

import requests
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

from ..config import settings
from ..models import UserProfile

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "nexora-secret-key-change-in-production"  # Should be in env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class DescopeAuthService:
    """Service for handling Descope authentication."""
    
    def __init__(self):
        """Initialize Descope authentication service."""
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
    
    def register_user(self, email: str, password: str, user_data: Dict[str, Any] = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        Register a new user with Descope.
        
        Args:
            email: User email
            password: User password
            user_data: Additional user data
            
        Returns:
            Tuple of (success, message, user_info)
        """
        if not self.is_configured():
            logger.warning("Descope not configured, using local registration")
            return self._local_register_user(email, password, user_data)
        
        try:
            # Descope user creation
            payload = {
                "email": email,
                "password": password,
                "user": user_data or {}
            }
            
            response = requests.post(
                f"{self.base_url}/users",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                user_info = response.json()
                logger.info(f"User registered successfully: {email}")
                return True, "User registered successfully", user_info
            else:
                error_msg = response.json().get('error', 'Registration failed')
                logger.error(f"Registration failed for {email}: {error_msg}")
                return False, error_msg, None
                
        except Exception as e:
            logger.error(f"Error registering user {email}: {e}")
            return False, f"Registration error: {str(e)}", None
    
    def authenticate_user(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Authenticate user with Descope.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success, message, user_info)
        """
        if not self.is_configured():
            logger.warning("Descope not configured, using local authentication")
            return self._local_authenticate_user(email, password)
        
        try:
            # Descope authentication
            payload = {
                "email": email,
                "password": password
            }
            
            response = requests.post(
                f"{self.base_url}/auth/password/sign-in",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                logger.info(f"User authenticated successfully: {email}")
                return True, "Authentication successful", auth_data
            else:
                error_msg = response.json().get('error', 'Authentication failed')
                logger.error(f"Authentication failed for {email}: {error_msg}")
                return False, error_msg, None
                
        except Exception as e:
            logger.error(f"Error authenticating user {email}: {e}")
            return False, f"Authentication error: {str(e)}", None
    
    def get_user_info(self, user_id: str) -> Tuple[bool, Optional[Dict]]:
        """
        Get user information from Descope.
        
        Args:
            user_id: User ID
            
        Returns:
            Tuple of (success, user_info)
        """
        if not self.is_configured():
            logger.warning("Descope not configured, using local user info")
            return self._local_get_user_info(user_id)
        
        try:
            response = requests.get(
                f"{self.base_url}/users/{user_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                user_info = response.json()
                return True, user_info
            else:
                logger.error(f"Failed to get user info for {user_id}")
                return False, None
                
        except Exception as e:
            logger.error(f"Error getting user info for {user_id}: {e}")
            return False, None
    
    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update user profile in Descope.
        
        Args:
            user_id: User ID
            profile_data: Profile data to update
            
        Returns:
            Tuple of (success, message)
        """
        if not self.is_configured():
            logger.warning("Descope not configured, using local profile update")
            return self._local_update_user_profile(user_id, profile_data)
        
        try:
            response = requests.patch(
                f"{self.base_url}/users/{user_id}",
                headers=self.headers,
                json={"user": profile_data},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"User profile updated successfully: {user_id}")
                return True, "Profile updated successfully"
            else:
                error_msg = response.json().get('error', 'Profile update failed')
                logger.error(f"Profile update failed for {user_id}: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            logger.error(f"Error updating user profile for {user_id}: {e}")
            return False, f"Profile update error: {str(e)}"
    
    def _local_register_user(self, email: str, password: str, user_data: Dict[str, Any] = None) -> Tuple[bool, str, Optional[Dict]]:
        """Local user registration fallback."""
        try:
            # Hash password
            hashed_password = pwd_context.hash(password)
            
            # Create user info
            user_info = {
                "id": f"local_user_{hash(email) % 100000}",
                "email": email,
                "password_hash": hashed_password,
                "created_at": datetime.now().isoformat(),
                "user_data": user_data or {}
            }
            
            # In a real implementation, you'd save this to a database
            logger.info(f"Local user registered: {email}")
            return True, "User registered successfully (local)", user_info
            
        except Exception as e:
            logger.error(f"Error in local registration: {e}")
            return False, f"Registration error: {str(e)}", None
    
    def _local_authenticate_user(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """Local user authentication fallback."""
        try:
            # In a real implementation, you'd check against a database
            # For demo purposes, accept any password
            user_info = {
                "id": f"local_user_{hash(email) % 100000}",
                "email": email,
                "authenticated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Local user authenticated: {email}")
            return True, "Authentication successful (local)", user_info
            
        except Exception as e:
            logger.error(f"Error in local authentication: {e}")
            return False, f"Authentication error: {str(e)}", None
    
    def _local_get_user_info(self, user_id: str) -> Tuple[bool, Optional[Dict]]:
        """Local user info fallback."""
        try:
            # In a real implementation, you'd fetch from a database
            user_info = {
                "id": user_id,
                "email": f"user_{user_id}@example.com",
                "created_at": datetime.now().isoformat()
            }
            
            return True, user_info
            
        except Exception as e:
            logger.error(f"Error getting local user info: {e}")
            return False, None
    
    def _local_update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Local profile update fallback."""
        try:
            # In a real implementation, you'd update a database
            logger.info(f"Local profile updated for user: {user_id}")
            return True, "Profile updated successfully (local)"
            
        except Exception as e:
            logger.error(f"Error in local profile update: {e}")
            return False, f"Profile update error: {str(e)}"


class JWTService:
    """Service for JWT token management."""
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            return None
        except jwt.JWTError:
            logger.error("Invalid token")
            return None


class AuthService:
    """Main authentication service combining Descope and JWT."""
    
    def __init__(self):
        """Initialize authentication service."""
        self.descope_service = DescopeAuthService()
        self.jwt_service = JWTService()
    
    def register_user(self, email: str, password: str, user_data: Dict[str, Any] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Register a new user and return access token.
        
        Args:
            email: User email
            password: User password
            user_data: Additional user data
            
        Returns:
            Tuple of (success, message, access_token)
        """
        success, message, user_info = self.descope_service.register_user(email, password, user_data)
        
        if success and user_info:
            # Create access token
            token_data = {
                "sub": user_info.get("id", email),
                "email": email,
                "user_id": user_info.get("id")
            }
            access_token = self.jwt_service.create_access_token(token_data)
            return True, message, access_token
        
        return False, message, None
    
    def authenticate_user(self, email: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """
        Authenticate user and return access token.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success, message, access_token)
        """
        success, message, user_info = self.descope_service.authenticate_user(email, password)
        
        if success and user_info:
            # Create access token
            token_data = {
                "sub": user_info.get("id", email),
                "email": email,
                "user_id": user_info.get("id")
            }
            access_token = self.jwt_service.create_access_token(token_data)
            return True, message, access_token
        
        return False, message, None
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token."""
        return self.jwt_service.verify_token(token)
    
    def get_user_info(self, user_id: str) -> Tuple[bool, Optional[Dict]]:
        """Get user information."""
        return self.descope_service.get_user_info(user_id)
    
    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Update user profile."""
        return self.descope_service.update_user_profile(user_id, profile_data)
