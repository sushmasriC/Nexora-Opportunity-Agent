"""
Personalization service for Nexora AI Agent.
Handles user-specific opportunity matching and recommendation generation.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import os
import json

from ..models import Opportunity, UserProfile, OpportunityType
from ..database.user_db import UserDatabase
from .cohere_service import CohereService
from .matching_engine import MatchingEngine

logger = logging.getLogger(__name__)


class PersonalizationService:
    """Service for personalized opportunity matching and recommendations."""
    
    def __init__(self, cohere_service: CohereService, user_db: UserDatabase):
        """
        Initialize personalization service.
        
        Args:
            cohere_service: CohereService instance
            user_db: UserDatabase instance
        """
        self.cohere_service = cohere_service
        self.user_db = user_db
        self.matching_engine = MatchingEngine(cohere_service)
        
        # Personalization thresholds
        self.high_similarity_threshold = 0.7  # Best matches
        self.medium_similarity_threshold = 0.4  # Good matches
        self.low_similarity_threshold = 0.2   # Other suggestions
    
    def process_user_onboarding(self, user_id: str, onboarding_data: Dict[str, Any]) -> bool:
        """
        Process user onboarding data and create initial profile.
        
        Args:
            user_id: User ID
            onboarding_data: Dictionary containing skills, interests, preferences, etc.
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Processing onboarding for user {user_id}")
            
            # Create user profile from onboarding data
            profile = UserProfile(
                user_id=user_id,
                email=onboarding_data.get('email', ''),
                skills=onboarding_data.get('skills', []),
                interests=onboarding_data.get('interests', []),
                experience_level=onboarding_data.get('experience_level'),
                preferred_locations=onboarding_data.get('preferred_locations', []),
                remote_preference=onboarding_data.get('remote_preference', True),
                resume_text=onboarding_data.get('resume_text', '')
            )
            
            # Save profile to database
            success = self.user_db.create_user_profile(profile)
            if not success:
                logger.error(f"Failed to save profile for user {user_id}")
                return False
            
            # Update user preferences
            preferences = {
                'notification_frequency': onboarding_data.get('notification_frequency', 'hourly'),
                'email_notifications': onboarding_data.get('email_notifications', True),
                'min_match_score': onboarding_data.get('min_match_score', 0.3),
                'max_results': onboarding_data.get('max_results', 15),
                'preferred_sources': onboarding_data.get('preferred_sources', [])
            }
            
            self.user_db.update_user_preferences(user_id, preferences)
            
            # Process resume if provided
            if onboarding_data.get('resume_path'):
                self._process_resume_upload(user_id, onboarding_data['resume_path'])
            
            logger.info(f"Onboarding completed successfully for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing onboarding for user {user_id}: {e}")
            return False
    
    def generate_personalized_recommendations(self, user_id: str, opportunities: List[Opportunity]) -> Dict[str, Any]:
        """
        Generate personalized recommendations for a user.
        
        Args:
            user_id: User ID
            opportunities: List of opportunities to match against
            
        Returns:
            Dictionary with recommendation results
        """
        try:
            logger.info(f"Generating personalized recommendations for user {user_id}")
            
            # Get user profile
            profile = self.user_db.get_user_profile(user_id)
            if not profile:
                logger.warning(f"No profile found for user {user_id}")
                return {"error": "User profile not found"}
            
            # Get user preferences
            preferences = self.user_db.get_user_preferences(user_id)
            min_score = preferences.get('min_match_score', 0.3) if preferences else 0.3
            
            # Find matches using the matching engine
            matches = self.matching_engine.find_matches(
                opportunities, profile, min_score, max_results=50
            )
            
            # Categorize matches by similarity score
            best_matches = []
            good_matches = []
            other_suggestions = []
            
            for match in matches:
                score = match.similarity_score
                
                if score >= self.high_similarity_threshold:
                    best_matches.append(match)
                elif score >= self.medium_similarity_threshold:
                    good_matches.append(match)
                elif score >= self.low_similarity_threshold:
                    other_suggestions.append(match)
            
            # Store recommendations in database
            recommendations_created = 0
            for match in matches:
                success = self.user_db.create_recommendation(
                    user_id=user_id,
                    opportunity_id=match.opportunity.id,
                    opportunity_type=match.opportunity.type.value,
                    similarity_score=match.similarity_score,
                    matched_skills=match.matched_skills,
                    matched_interests=match.matched_interests,
                    reasoning=match.reasoning
                )
                if success:
                    recommendations_created += 1
            
            result = {
                "user_id": user_id,
                "total_opportunities": len(opportunities),
                "total_matches": len(matches),
                "recommendations_created": recommendations_created,
                "best_matches": len(best_matches),
                "good_matches": len(good_matches),
                "other_suggestions": len(other_suggestions),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Generated {len(matches)} recommendations for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {e}")
            return {"error": str(e)}
    
    def get_segregated_recommendations(self, user_id: str, limit: int = 20) -> Dict[str, Any]:
        """
        Get segregated recommendations (best matches vs other suggestions).
        
        Args:
            user_id: User ID
            limit: Maximum number of recommendations per category
            
        Returns:
            Dictionary with segregated recommendations
        """
        try:
            # Get best matches (high similarity)
            best_matches = self.user_db.get_user_recommendations(
                user_id, limit=limit, min_score=self.high_similarity_threshold
            )
            
            # Get other suggestions (medium and low similarity)
            other_suggestions = self.user_db.get_user_recommendations(
                user_id, limit=limit*2, min_score=self.low_similarity_threshold
            )
            
            # Filter out best matches from other suggestions
            best_match_ids = {match['opportunity_id'] for match in best_matches}
            other_suggestions = [
                match for match in other_suggestions 
                if match['opportunity_id'] not in best_match_ids
            ][:limit]
            
            return {
                "best_matches": best_matches,
                "other_suggestions": other_suggestions,
                "total_best_matches": len(best_matches),
                "total_other_suggestions": len(other_suggestions),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting segregated recommendations for user {user_id}: {e}")
            return {"error": str(e)}
    
    def get_weekly_summary_data(self, user_id: str) -> Dict[str, Any]:
        """
        Get data for weekly summary email.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with weekly summary data
        """
        try:
            # Get top 5 job matches from the last week
            job_matches = self.user_db.get_user_recommendations(
                user_id, limit=5, opportunity_type="job", min_score=0.3
            )
            
            # Get top 3 hackathon matches from the last week
            hackathon_matches = self.user_db.get_user_recommendations(
                user_id, limit=3, opportunity_type="hackathon", min_score=0.3
            )
            
            # Get user profile for personalization
            profile = self.user_db.get_user_profile(user_id)
            user_data = self.user_db.get_user(user_id)
            
            return {
                "user_id": user_id,
                "user_email": user_data['email'] if user_data else '',
                "user_name": profile.experience_level if profile else 'User',
                "top_job_matches": job_matches,
                "top_hackathon_matches": hackathon_matches,
                "total_job_matches": len(job_matches),
                "total_hackathon_matches": len(hackathon_matches),
                "week_start": (datetime.now() - timedelta(days=7)).isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting weekly summary data for user {user_id}: {e}")
            return {"error": str(e)}
    
    def update_user_engagement(self, user_id: str, opportunity_id: str, action: str) -> bool:
        """
        Update user engagement with recommendations.
        
        Args:
            user_id: User ID
            opportunity_id: Opportunity ID
            action: Action taken ('viewed', 'applied', 'dismissed')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get recommendation by user_id and opportunity_id
            recommendations = self.user_db.get_user_recommendations(user_id, limit=1000)
            recommendation = next(
                (rec for rec in recommendations if rec['opportunity_id'] == opportunity_id), 
                None
            )
            
            if not recommendation:
                logger.warning(f"Recommendation not found for user {user_id}, opportunity {opportunity_id}")
                return False
            
            # Update based on action
            if action == 'viewed':
                return self.user_db.mark_recommendation_viewed(recommendation['id'])
            elif action == 'applied':
                return self.user_db.mark_recommendation_applied(recommendation['id'])
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user engagement: {e}")
            return False
    
    def _process_resume_upload(self, user_id: str, resume_path: str) -> bool:
        """
        Process resume upload and extract text for embedding.
        
        Args:
            user_id: User ID
            resume_path: Path to uploaded resume file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # For now, just store the file path
            # In a real implementation, you would:
            # 1. Extract text from PDF
            # 2. Generate embedding using Cohere
            # 3. Store embedding in database
            
            file_name = os.path.basename(resume_path)
            file_size = os.path.getsize(resume_path) if os.path.exists(resume_path) else 0
            
            # Record resume upload
            success = self.user_db.upload_resume(user_id, resume_path, file_name, file_size)
            
            if success:
                logger.info(f"Resume processed for user {user_id}: {file_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing resume for user {user_id}: {e}")
            return False
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get user analytics and insights.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user analytics
        """
        try:
            # Get all recommendations for the user
            all_recommendations = self.user_db.get_user_recommendations(user_id, limit=1000)
            
            if not all_recommendations:
                return {
                    "user_id": user_id,
                    "total_recommendations": 0,
                    "analytics": {}
                }
            
            # Calculate analytics
            total_recommendations = len(all_recommendations)
            viewed_count = sum(1 for rec in all_recommendations if rec['is_viewed'])
            applied_count = sum(1 for rec in all_recommendations if rec['is_applied'])
            
            # Average similarity score
            avg_similarity = sum(rec['similarity_score'] for rec in all_recommendations) / total_recommendations
            
            # Top matched skills
            all_skills = []
            for rec in all_recommendations:
                all_skills.extend(rec['matched_skills'])
            
            skill_counts = {}
            for skill in all_skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
            
            top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Opportunity type distribution
            type_counts = {}
            for rec in all_recommendations:
                opp_type = rec['opportunity_type']
                type_counts[opp_type] = type_counts.get(opp_type, 0) + 1
            
            return {
                "user_id": user_id,
                "total_recommendations": total_recommendations,
                "viewed_count": viewed_count,
                "applied_count": applied_count,
                "view_rate": viewed_count / total_recommendations if total_recommendations > 0 else 0,
                "application_rate": applied_count / total_recommendations if total_recommendations > 0 else 0,
                "average_similarity_score": avg_similarity,
                "top_matched_skills": top_skills,
                "opportunity_type_distribution": type_counts,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting user analytics for user {user_id}: {e}")
            return {"error": str(e)}
