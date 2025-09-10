"""
User database models and operations for Nexora AI Agent.
Handles user profile storage, retrieval, and management.
"""

import sqlite3
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from ..models import UserProfile

logger = logging.getLogger(__name__)


class UserDatabase:
    """Database service for user management."""
    
    def __init__(self, db_path: str = "nexora_users.db"):
        """
        Initialize user database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id TEXT PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1
                    )
                """)
                
                # Create user_profiles table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        skills TEXT,  -- JSON array
                        interests TEXT,  -- JSON array
                        experience_level TEXT,
                        preferred_locations TEXT,  -- JSON array
                        remote_preference BOOLEAN DEFAULT 1,
                        resume_text TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                # Create user_preferences table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        notification_frequency TEXT DEFAULT 'hourly',
                        email_notifications BOOLEAN DEFAULT 1,
                        min_match_score REAL DEFAULT 0.3,
                        max_results INTEGER DEFAULT 15,
                        preferred_sources TEXT,  -- JSON array
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                # Create user_sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        session_token TEXT UNIQUE NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                # Create recommendations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS recommendations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        opportunity_id TEXT NOT NULL,
                        opportunity_type TEXT NOT NULL,
                        similarity_score REAL NOT NULL,
                        matched_skills TEXT,  -- JSON array
                        matched_interests TEXT,  -- JSON array
                        reasoning TEXT,
                        is_viewed BOOLEAN DEFAULT 0,
                        is_applied BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        UNIQUE(user_id, opportunity_id)
                    )
                """)
                
                # Create resume_uploads table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS resume_uploads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        file_name TEXT NOT NULL,
                        file_size INTEGER,
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_processed BOOLEAN DEFAULT 0,
                        embedding_data TEXT,  -- JSON for resume embedding
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def create_user(self, user_id: str, email: str, password_hash: str = None) -> bool:
        """
        Create a new user.
        
        Args:
            user_id: Unique user ID
            email: User email
            password_hash: Hashed password (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO users (id, email, password_hash)
                    VALUES (?, ?, ?)
                """, (user_id, email, password_hash))
                
                # Create default preferences
                cursor.execute("""
                    INSERT INTO user_preferences (user_id)
                    VALUES (?)
                """, (user_id,))
                
                conn.commit()
                logger.info(f"User created successfully: {user_id}")
                return True
                
        except sqlite3.IntegrityError:
            logger.error(f"User already exists: {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User data or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, email, created_at, updated_at, is_active
                    FROM users WHERE id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "email": row[1],
                        "created_at": row[2],
                        "updated_at": row[3],
                        "is_active": bool(row[4])
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User data or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, email, password_hash, created_at, updated_at, is_active
                    FROM users WHERE email = ?
                """, (email,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "email": row[1],
                        "password_hash": row[2],
                        "created_at": row[3],
                        "updated_at": row[4],
                        "is_active": bool(row[5])
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update user data.
        
        Args:
            user_id: User ID
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build dynamic update query
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    if key in ['email', 'password_hash', 'is_active']:
                        set_clauses.append(f"{key} = ?")
                        values.append(value)
                
                if not set_clauses:
                    return False
                
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                values.append(user_id)
                
                query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?"
                cursor.execute(query, values)
                
                conn.commit()
                logger.info(f"User updated successfully: {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False
    
    def create_user_profile(self, user_profile: UserProfile) -> bool:
        """
        Create or update user profile.
        
        Args:
            user_profile: UserProfile object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if profile exists
                cursor.execute("""
                    SELECT id FROM user_profiles WHERE user_id = ?
                """, (user_profile.user_id,))
                
                existing_profile = cursor.fetchone()
                
                if existing_profile:
                    # Update existing profile
                    cursor.execute("""
                        UPDATE user_profiles SET
                            skills = ?,
                            interests = ?,
                            experience_level = ?,
                            preferred_locations = ?,
                            remote_preference = ?,
                            resume_text = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    """, (
                        json.dumps(user_profile.skills),
                        json.dumps(user_profile.interests),
                        user_profile.experience_level,
                        json.dumps(user_profile.preferred_locations),
                        user_profile.remote_preference,
                        user_profile.resume_text,
                        user_profile.user_id
                    ))
                else:
                    # Create new profile
                    cursor.execute("""
                        INSERT INTO user_profiles (
                            user_id, skills, interests, experience_level,
                            preferred_locations, remote_preference, resume_text
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user_profile.user_id,
                        json.dumps(user_profile.skills),
                        json.dumps(user_profile.interests),
                        user_profile.experience_level,
                        json.dumps(user_profile.preferred_locations),
                        user_profile.remote_preference,
                        user_profile.resume_text
                    ))
                
                conn.commit()
                logger.info(f"User profile saved successfully: {user_profile.user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving user profile {user_profile.user_id}: {e}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user profile by user ID.
        
        Args:
            user_id: User ID
            
        Returns:
            UserProfile object or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT user_id, skills, interests, experience_level,
                           preferred_locations, remote_preference, resume_text,
                           created_at, updated_at
                    FROM user_profiles WHERE user_id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return UserProfile(
                        user_id=row[0],
                        email="",  # Will be filled from users table if needed
                        skills=json.loads(row[1]) if row[1] else [],
                        interests=json.loads(row[2]) if row[2] else [],
                        experience_level=row[3],
                        preferred_locations=json.loads(row[4]) if row[4] else [],
                        remote_preference=bool(row[5]),
                        resume_text=row[6],
                        created_at=datetime.fromisoformat(row[7]) if row[7] else datetime.now(),
                        updated_at=datetime.fromisoformat(row[8]) if row[8] else datetime.now()
                    )
                return None
                
        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {e}")
            return None
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user preferences.
        
        Args:
            user_id: User ID
            
        Returns:
            User preferences or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT notification_frequency, email_notifications, min_match_score,
                           max_results, preferred_sources, created_at, updated_at
                    FROM user_preferences WHERE user_id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "notification_frequency": row[0],
                        "email_notifications": bool(row[1]),
                        "min_match_score": row[2],
                        "max_results": row[3],
                        "preferred_sources": json.loads(row[4]) if row[4] else [],
                        "created_at": row[5],
                        "updated_at": row[6]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting user preferences {user_id}: {e}")
            return None
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences.
        
        Args:
            user_id: User ID
            preferences: Dictionary of preferences to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build dynamic update query
                set_clauses = []
                values = []
                
                for key, value in preferences.items():
                    if key in ['notification_frequency', 'email_notifications', 'min_match_score', 'max_results', 'preferred_sources']:
                        if key == 'preferred_sources':
                            set_clauses.append(f"{key} = ?")
                            values.append(json.dumps(value))
                        else:
                            set_clauses.append(f"{key} = ?")
                            values.append(value)
                
                if not set_clauses:
                    return False
                
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                values.append(user_id)
                
                query = f"UPDATE user_preferences SET {', '.join(set_clauses)} WHERE user_id = ?"
                cursor.execute(query, values)
                
                conn.commit()
                logger.info(f"User preferences updated successfully: {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating user preferences {user_id}: {e}")
            return False
    
    def create_session(self, user_id: str, session_token: str, expires_at: datetime) -> bool:
        """
        Create user session.
        
        Args:
            user_id: User ID
            session_token: Session token
            expires_at: Expiration time
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO user_sessions (user_id, session_token, expires_at)
                    VALUES (?, ?, ?)
                """, (user_id, session_token, expires_at.isoformat()))
                
                conn.commit()
                logger.info(f"Session created successfully for user: {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating session for user {user_id}: {e}")
            return False
    
    def validate_session(self, session_token: str) -> Optional[str]:
        """
        Validate session token and return user ID.
        
        Args:
            session_token: Session token
            
        Returns:
            User ID if valid, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT user_id FROM user_sessions 
                    WHERE session_token = ? AND expires_at > CURRENT_TIMESTAMP
                """, (session_token,))
                
                row = cursor.fetchone()
                if row:
                    return row[0]
                return None
                
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return None
    
    def delete_session(self, session_token: str) -> bool:
        """
        Delete user session.
        
        Args:
            session_token: Session token
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM user_sessions WHERE session_token = ?
                """, (session_token,))
                
                conn.commit()
                logger.info(f"Session deleted successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions deleted
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM user_sessions WHERE expires_at <= CURRENT_TIMESTAMP
                """)
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired sessions")
                
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get all users (for admin purposes).
        
        Returns:
            List of user data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, email, created_at, updated_at, is_active
                    FROM users ORDER BY created_at DESC
                """)
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        "id": row[0],
                        "email": row[1],
                        "created_at": row[2],
                        "updated_at": row[3],
                        "is_active": bool(row[4])
                    })
                
                return users
                
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete user and all associated data.
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete in order to respect foreign key constraints
                cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM recommendations WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM resume_uploads WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM user_preferences WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM user_profiles WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                
                conn.commit()
                logger.info(f"User deleted successfully: {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    # Recommendation management methods
    def create_recommendation(self, user_id: str, opportunity_id: str, opportunity_type: str,
                            similarity_score: float, matched_skills: List[str] = None,
                            matched_interests: List[str] = None, reasoning: str = "") -> bool:
        """
        Create a new recommendation.
        
        Args:
            user_id: User ID
            opportunity_id: Opportunity ID
            opportunity_type: Type of opportunity (job, internship, hackathon)
            similarity_score: Similarity score (0.0 to 1.0)
            matched_skills: List of matched skills
            matched_interests: List of matched interests
            reasoning: Reasoning for the match
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO recommendations 
                    (user_id, opportunity_id, opportunity_type, similarity_score, 
                     matched_skills, matched_interests, reasoning, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    user_id, opportunity_id, opportunity_type, similarity_score,
                    json.dumps(matched_skills or []),
                    json.dumps(matched_interests or []),
                    reasoning
                ))
                
                conn.commit()
                logger.info(f"Recommendation created for user {user_id}: {opportunity_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating recommendation: {e}")
            return False
    
    def get_user_recommendations(self, user_id: str, limit: int = 20, 
                               opportunity_type: str = None, min_score: float = 0.0) -> List[Dict[str, Any]]:
        """
        Get user recommendations.
        
        Args:
            user_id: User ID
            limit: Maximum number of recommendations
            opportunity_type: Filter by opportunity type
            min_score: Minimum similarity score
            
        Returns:
            List of recommendation data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, opportunity_id, opportunity_type, similarity_score,
                           matched_skills, matched_interests, reasoning, is_viewed,
                           is_applied, created_at, updated_at
                    FROM recommendations 
                    WHERE user_id = ? AND similarity_score >= ?
                """
                params = [user_id, min_score]
                
                if opportunity_type:
                    query += " AND opportunity_type = ?"
                    params.append(opportunity_type)
                
                query += " ORDER BY similarity_score DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                
                recommendations = []
                for row in cursor.fetchall():
                    recommendations.append({
                        "id": row[0],
                        "opportunity_id": row[1],
                        "opportunity_type": row[2],
                        "similarity_score": row[3],
                        "matched_skills": json.loads(row[4]) if row[4] else [],
                        "matched_interests": json.loads(row[5]) if row[5] else [],
                        "reasoning": row[6],
                        "is_viewed": bool(row[7]),
                        "is_applied": bool(row[8]),
                        "created_at": row[9],
                        "updated_at": row[10]
                    })
                
                return recommendations
                
        except Exception as e:
            logger.error(f"Error getting user recommendations: {e}")
            return []
    
    def mark_recommendation_viewed(self, recommendation_id: int) -> bool:
        """Mark a recommendation as viewed."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE recommendations 
                    SET is_viewed = 1, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (recommendation_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error marking recommendation as viewed: {e}")
            return False
    
    def mark_recommendation_applied(self, recommendation_id: int) -> bool:
        """Mark a recommendation as applied."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE recommendations 
                    SET is_applied = 1, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (recommendation_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error marking recommendation as applied: {e}")
            return False
    
    # Resume upload management methods
    def upload_resume(self, user_id: str, file_path: str, file_name: str, 
                     file_size: int) -> bool:
        """
        Record resume upload.
        
        Args:
            user_id: User ID
            file_path: Path to uploaded file
            file_name: Original file name
            file_size: File size in bytes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO resume_uploads (user_id, file_path, file_name, file_size)
                    VALUES (?, ?, ?, ?)
                """, (user_id, file_path, file_name, file_size))
                
                conn.commit()
                logger.info(f"Resume uploaded for user {user_id}: {file_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error uploading resume: {e}")
            return False
    
    def get_user_resumes(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's uploaded resumes."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, file_path, file_name, file_size, upload_date, is_processed
                    FROM resume_uploads WHERE user_id = ?
                    ORDER BY upload_date DESC
                """, (user_id,))
                
                resumes = []
                for row in cursor.fetchall():
                    resumes.append({
                        "id": row[0],
                        "file_path": row[1],
                        "file_name": row[2],
                        "file_size": row[3],
                        "upload_date": row[4],
                        "is_processed": bool(row[5])
                    })
                
                return resumes
                
        except Exception as e:
            logger.error(f"Error getting user resumes: {e}")
            return []
    
    def update_resume_embedding(self, resume_id: int, embedding_data: str) -> bool:
        """Update resume with embedding data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE resume_uploads 
                    SET embedding_data = ?, is_processed = 1 
                    WHERE id = ?
                """, (embedding_data, resume_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error updating resume embedding: {e}")
            return False
