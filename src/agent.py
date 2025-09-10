"""
Main Nexora AI Agent class that orchestrates the entire workflow.
Coordinates fetching, matching, and notification processes.
"""

import logging
from typing import List, Optional
from datetime import datetime

from .models import UserProfile, MatchResult, OpportunityType
from .services.cohere_service import CohereService
from .services.opportunity_fetchers import OpportunityFetcherManager
from .services.matching_engine import MatchingEngine
from .services.email_service import EmailService
from .services.cache_service import CacheService

logger = logging.getLogger(__name__)


class NexoraAgent:
    """Main AI agent for finding and matching opportunities."""
    
    def __init__(self):
        """Initialize the Nexora agent with all required services."""
        logger.info("Initializing Nexora AI Agent...")
        
        # Initialize services
        self.cache_service = CacheService()
        self.cohere_service = CohereService()
        self.opportunity_fetcher = OpportunityFetcherManager()
        self.matching_engine = MatchingEngine(self.cohere_service)
        self.email_service = EmailService()
        
        logger.info("Nexora AI Agent initialized successfully")
        logger.info(f"Cache service: {self.cache_service.get_cache_stats()}")
    
    def create_sample_user_profile(self, user_id: str = "demo_user", email: str = "demo@example.com") -> UserProfile:
        """
        Create a sample user profile for demonstration.
        
        Args:
            user_id: User ID
            email: User email
            
        Returns:
            UserProfile object
        """
        return UserProfile(
            user_id=user_id,
            email=email,
            skills=[
                "Python", "JavaScript", "React", "Node.js", "AWS", 
                "Machine Learning", "Data Science", "Docker", "Git"
            ],
            interests=[
                "Artificial Intelligence", "Web Development", "Startups", 
                "Open Source", "Tech Innovation", "Remote Work"
            ],
            experience_level="Mid-level",
            preferred_locations=["Remote", "Bangalore", "Hyderabad"],
            remote_preference=True,
            resume_text="Experienced software engineer with 3+ years in full-stack development. "
                       "Passionate about AI/ML and building scalable web applications. "
                       "Strong background in Python, JavaScript, and cloud technologies."
        )
    
    def fetch_opportunities(self, limit_per_source: int = 15) -> List:
        """
        Fetch opportunities from all sources.
        
        Args:
            limit_per_source: Maximum opportunities to fetch from each source
            
        Returns:
            List of Opportunity objects
        """
        logger.info(f"Fetching opportunities (limit: {limit_per_source} per source)")
        opportunities = self.opportunity_fetcher.fetch_all_opportunities(limit_per_source)
        logger.info(f"Successfully fetched {len(opportunities)} total opportunities")
        return opportunities
    
    def find_matches_for_user(self, profile: UserProfile, opportunities: List,
                            min_score: float = 0.3, max_results: int = 15) -> List[MatchResult]:
        """
        Find matching opportunities for a user profile.
        
        Args:
            profile: User profile to match with
            opportunities: List of opportunities to match against
            min_score: Minimum similarity score threshold
            max_results: Maximum number of results to return
            
        Returns:
            List of MatchResult objects
        """
        logger.info(f"Finding matches for user {profile.user_id}")
        matches = self.matching_engine.find_matches(
            opportunities, profile, min_score, max_results
        )
        logger.info(f"Found {len(matches)} matches for user {profile.user_id}")
        return matches
    
    def send_notification_email(self, matches: List[MatchResult], user_email: str) -> bool:
        """
        Send email notification with matched opportunities.
        
        Args:
            matches: List of MatchResult objects
            user_email: User's email address
            
        Returns:
            True if email sent successfully, False otherwise
        """
        logger.info(f"Sending notification email to {user_email} with {len(matches)} matches")
        success = self.email_service.send_opportunities_email(matches, user_email)
        
        if success:
            logger.info(f"Email sent successfully to {user_email}")
        else:
            logger.error(f"Failed to send email to {user_email}")
        
        return success
    
    def send_test_email(self, user_email: str) -> bool:
        """
        Send a test email to verify email service.
        
        Args:
            user_email: User's email address
            
        Returns:
            True if email sent successfully, False otherwise
        """
        logger.info(f"Sending test email to {user_email}")
        success = self.email_service.send_test_email(user_email)
        
        if success:
            logger.info(f"Test email sent successfully to {user_email}")
        else:
            logger.error(f"Failed to send test email to {user_email}")
        
        return success
    
    def run_full_workflow(self, user_profile: UserProfile, 
                         limit_per_source: int = 15, 
                         min_score: float = 0.3,
                         max_results: int = 15) -> dict:
        """
        Run the complete workflow: fetch -> match -> notify.
        
        Args:
            user_profile: User profile to process
            limit_per_source: Maximum opportunities to fetch from each source
            min_score: Minimum similarity score threshold
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with workflow results and statistics
        """
        logger.info(f"Starting full workflow for user {user_profile.user_id}")
        start_time = datetime.now()
        
        try:
            # Step 1: Fetch opportunities
            logger.info("Step 1: Fetching opportunities...")
            opportunities = self.fetch_opportunities(limit_per_source)
            
            # Step 2: Find matches
            logger.info("Step 2: Finding matches...")
            matches = self.find_matches_for_user(user_profile, opportunities, min_score, max_results)
            
            # Step 3: Send notification
            logger.info("Step 3: Sending notification...")
            email_sent = self.send_notification_email(matches, user_profile.email)
            
            # Calculate statistics
            match_stats = self.matching_engine.get_match_statistics(matches)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                "success": True,
                "user_id": user_profile.user_id,
                "total_opportunities": len(opportunities),
                "matches_found": len(matches),
                "email_sent": email_sent,
                "match_statistics": match_stats,
                "duration_seconds": duration,
                "timestamp": end_time.isoformat()
            }
            
            logger.info(f"Workflow completed successfully in {duration:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Error in workflow: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_opportunities_by_type(self, opportunity_type: OpportunityType, limit: int = 20) -> List:
        """
        Get opportunities of a specific type.
        
        Args:
            opportunity_type: Type of opportunities to fetch
            limit: Maximum number of opportunities to fetch
            
        Returns:
            List of Opportunity objects of the specified type
        """
        logger.info(f"Fetching {opportunity_type.value} opportunities (limit: {limit})")
        opportunities = self.opportunity_fetcher.fetch_opportunities_by_type(opportunity_type, limit)
        logger.info(f"Fetched {len(opportunities)} {opportunity_type.value} opportunities")
        return opportunities
    
    def analyze_user_profile(self, profile: UserProfile) -> dict:
        """
        Analyze a user profile and provide insights.
        
        Args:
            profile: UserProfile object to analyze
            
        Returns:
            Dictionary with profile analysis
        """
        logger.info(f"Analyzing profile for user {profile.user_id}")
        
        analysis = {
            "user_id": profile.user_id,
            "skills_count": len(profile.skills),
            "interests_count": len(profile.interests),
            "preferred_locations_count": len(profile.preferred_locations),
            "has_resume": bool(profile.resume_text),
            "experience_level": profile.experience_level,
            "remote_preference": profile.remote_preference,
            "profile_completeness": self._calculate_profile_completeness(profile),
            "recommended_opportunity_types": self._recommend_opportunity_types(profile)
        }
        
        logger.info(f"Profile analysis completed for user {profile.user_id}")
        return analysis
    
    def _calculate_profile_completeness(self, profile: UserProfile) -> float:
        """Calculate how complete a user profile is."""
        total_fields = 7  # Total number of profile fields
        filled_fields = 0
        
        if profile.skills:
            filled_fields += 1
        if profile.interests:
            filled_fields += 1
        if profile.experience_level:
            filled_fields += 1
        if profile.preferred_locations:
            filled_fields += 1
        if profile.resume_text:
            filled_fields += 1
        if profile.remote_preference is not None:
            filled_fields += 1
        if profile.email:
            filled_fields += 1
        
        return filled_fields / total_fields
    
    def _recommend_opportunity_types(self, profile: UserProfile) -> List[str]:
        """Recommend opportunity types based on user profile."""
        recommendations = []
        
        # Analyze skills for recommendations
        tech_skills = ["python", "javascript", "react", "node.js", "aws", "docker", "kubernetes"]
        ai_skills = ["machine learning", "data science", "ai", "artificial intelligence"]
        
        user_skills_lower = [skill.lower() for skill in profile.skills]
        
        if any(skill in user_skills_lower for skill in tech_skills):
            recommendations.append("job")
        
        if any(skill in user_skills_lower for skill in ai_skills):
            recommendations.append("hackathon")
        
        # Always recommend internships for entry-level users
        if profile.experience_level and "entry" in profile.experience_level.lower():
            recommendations.append("internship")
        
        # If no specific recommendations, suggest all types
        if not recommendations:
            recommendations = ["job", "internship", "hackathon"]
        
        return list(set(recommendations))  # Remove duplicates
