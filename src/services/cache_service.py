"""
Cache service for storing and retrieving opportunities and user data.
Supports both Redis and local memory caching.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import hashlib

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from ..config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Service for caching data with Redis or local memory fallback."""
    
    def __init__(self):
        """Initialize cache service."""
        self.redis_client = None
        self.local_cache = {}
        self.cache_ttl = 3600  # 1 hour default TTL
        
        if REDIS_AVAILABLE and settings.redis_url:
            try:
                self.redis_client = redis.from_url(settings.redis_url)
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Using local cache.")
                self.redis_client = None
        else:
            logger.info("Redis not available, using local cache")
    
    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Generate a cache key."""
        return f"nexora:{prefix}:{identifier}"
    
    def _serialize_data(self, data: Any) -> str:
        """Serialize data for storage."""
        if isinstance(data, (dict, list)):
            return json.dumps(data, default=str)
        return str(data)
    
    def _deserialize_data(self, data: str) -> Any:
        """Deserialize data from storage."""
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return data
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            serialized_value = self._serialize_data(value)
            ttl = ttl or self.cache_ttl
            
            if self.redis_client:
                self.redis_client.setex(key, ttl, serialized_value)
            else:
                # Local cache with TTL
                self.local_cache[key] = {
                    'value': serialized_value,
                    'expires': datetime.now() + timedelta(seconds=ttl)
                }
            
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return self._deserialize_data(value.decode('utf-8'))
            else:
                # Local cache
                if key in self.local_cache:
                    cache_entry = self.local_cache[key]
                    if datetime.now() < cache_entry['expires']:
                        return self._deserialize_data(cache_entry['value'])
                    else:
                        # Expired, remove from cache
                        del self.local_cache[key]
            
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.local_cache.pop(key, None)
            
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            if self.redis_client:
                # Clear all nexora keys
                keys = self.redis_client.keys("nexora:*")
                if keys:
                    self.redis_client.delete(*keys)
            else:
                # Clear local cache
                self.local_cache.clear()
            
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def cache_opportunities(self, source: str, opportunities: List[Dict[str, Any]], ttl: int = 3600) -> bool:
        """
        Cache opportunities from a specific source.
        
        Args:
            source: Source name (e.g., 'wellfound', 'indeed')
            opportunities: List of opportunity data
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        key = self._generate_key("opportunities", source)
        return self.set(key, opportunities, ttl)
    
    def get_cached_opportunities(self, source: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached opportunities from a specific source.
        
        Args:
            source: Source name
            
        Returns:
            Cached opportunities or None
        """
        key = self._generate_key("opportunities", source)
        return self.get(key)
    
    def cache_user_matches(self, user_id: str, matches: List[Dict[str, Any]], ttl: int = 1800) -> bool:
        """
        Cache user matches.
        
        Args:
            user_id: User ID
            matches: List of match data
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        key = self._generate_key("matches", user_id)
        return self.set(key, matches, ttl)
    
    def get_cached_user_matches(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached user matches.
        
        Args:
            user_id: User ID
            
        Returns:
            Cached matches or None
        """
        key = self._generate_key("matches", user_id)
        return self.get(key)
    
    def cache_user_profile(self, user_id: str, profile: Dict[str, Any], ttl: int = 7200) -> bool:
        """
        Cache user profile.
        
        Args:
            user_id: User ID
            profile: User profile data
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        key = self._generate_key("profile", user_id)
        return self.set(key, profile, ttl)
    
    def get_cached_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached user profile.
        
        Args:
            user_id: User ID
            
        Returns:
            Cached profile or None
        """
        key = self._generate_key("profile", user_id)
        return self.get(key)
    
    def generate_profile_hash(self, profile_data: Dict[str, Any]) -> str:
        """
        Generate a hash for profile data to detect changes.
        
        Args:
            profile_data: User profile data
            
        Returns:
            Hash string
        """
        # Create a stable representation for hashing
        stable_data = {
            'skills': sorted(profile_data.get('skills', [])),
            'interests': sorted(profile_data.get('interests', [])),
            'experience_level': profile_data.get('experience_level', ''),
            'preferred_locations': sorted(profile_data.get('preferred_locations', [])),
            'remote_preference': profile_data.get('remote_preference', True)
        }
        
        data_string = json.dumps(stable_data, sort_keys=True)
        return hashlib.md5(data_string.encode()).hexdigest()
    
    def is_cache_available(self) -> bool:
        """Check if cache is available."""
        return self.redis_client is not None or True  # Local cache is always available
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            'type': 'redis' if self.redis_client else 'local',
            'available': self.is_cache_available()
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats.update({
                    'redis_version': info.get('redis_version'),
                    'used_memory': info.get('used_memory_human'),
                    'connected_clients': info.get('connected_clients'),
                    'total_commands_processed': info.get('total_commands_processed')
                })
            except Exception as e:
                stats['error'] = str(e)
        else:
            stats['local_cache_size'] = len(self.local_cache)
        
        return stats
