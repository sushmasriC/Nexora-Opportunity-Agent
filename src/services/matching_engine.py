"""
Matching engine for finding relevant opportunities using Cohere embeddings.
Handles similarity calculations and opportunity ranking.
"""

import logging
from typing import List, Tuple, Dict
from datetime import datetime

from ..models import Opportunity, UserProfile, MatchResult, OpportunityType
from .cohere_service import CohereService

logger = logging.getLogger(__name__)


class MatchingEngine:
    """Engine for matching opportunities with user profiles using embeddings."""
    
    def __init__(self, cohere_service: CohereService):
        """
        Initialize the matching engine.
        
        Args:
            cohere_service: CohereService instance for embeddings
        """
        self.cohere_service = cohere_service
        self.min_similarity_threshold = 0.3  # Minimum similarity score to consider a match
    
    def calculate_skill_overlap(self, user_skills: List[str], required_skills: List[str]) -> Tuple[List[str], float]:
        """
        Calculate skill overlap between user and opportunity.
        
        Args:
            user_skills: List of user's skills
            required_skills: List of required skills for opportunity
            
        Returns:
            Tuple of (matched_skills, overlap_percentage)
        """
        if not required_skills:
            return [], 1.0  # If no skills required, consider it a perfect match
        
        user_skills_lower = [skill.lower().strip() for skill in user_skills]
        required_skills_lower = [skill.lower().strip() for skill in required_skills]
        
        matched_skills = []
        for req_skill in required_skills_lower:
            for user_skill in user_skills_lower:
                if req_skill in user_skill or user_skill in req_skill:
                    matched_skills.append(req_skill)
                    break
        
        overlap_percentage = len(matched_skills) / len(required_skills)
        return matched_skills, overlap_percentage
    
    def calculate_interest_overlap(self, user_interests: List[str], opportunity_text: str) -> Tuple[List[str], float]:
        """
        Calculate interest overlap between user and opportunity.
        
        Args:
            user_interests: List of user's interests
            opportunity_text: Text description of the opportunity
            
        Returns:
            Tuple of (matched_interests, overlap_percentage)
        """
        if not user_interests:
            return [], 0.0
        
        opportunity_text_lower = opportunity_text.lower()
        matched_interests = []
        
        for interest in user_interests:
            interest_lower = interest.lower().strip()
            if interest_lower in opportunity_text_lower:
                matched_interests.append(interest)
        
        overlap_percentage = len(matched_interests) / len(user_interests)
        return matched_interests, overlap_percentage
    
    def generate_match_reasoning(self, match: MatchResult) -> str:
        """
        Generate human-readable reasoning for why an opportunity matches.
        
        Args:
            match: MatchResult object
            
        Returns:
            Reasoning string
        """
        reasoning_parts = []
        
        # Skill matching reasoning
        if match.matched_skills:
            reasoning_parts.append(f"Your skills in {', '.join(match.matched_skills)} align well with this opportunity.")
        
        # Interest matching reasoning
        if match.matched_interests:
            reasoning_parts.append(f"This opportunity matches your interests in {', '.join(match.matched_interests)}.")
        
        # Experience level reasoning
        if match.opportunity.experience_level and match.user_profile.experience_level:
            if match.opportunity.experience_level.lower() in match.user_profile.experience_level.lower():
                reasoning_parts.append("The experience level requirement matches your background.")
        
        # Location reasoning
        if match.opportunity.location and match.user_profile.preferred_locations:
            if any(loc.lower() in match.opportunity.location.lower() 
                   for loc in match.user_profile.preferred_locations):
                reasoning_parts.append("The location matches your preferences.")
        
        # Remote work reasoning
        if match.opportunity.remote and match.user_profile.remote_preference:
            reasoning_parts.append("This is a remote opportunity, which matches your preference.")
        
        # Similarity score reasoning
        if match.similarity_score > 0.8:
            reasoning_parts.append("This is an excellent match based on your profile.")
        elif match.similarity_score > 0.6:
            reasoning_parts.append("This is a good match for your profile.")
        elif match.similarity_score > 0.4:
            reasoning_parts.append("This opportunity has some alignment with your profile.")
        
        return " ".join(reasoning_parts) if reasoning_parts else "This opportunity may be of interest based on your profile."
    
    def match_opportunity_with_profile(self, opportunity: Opportunity, profile: UserProfile) -> MatchResult:
        """
        Match a single opportunity with a user profile.
        
        Args:
            opportunity: Opportunity object
            profile: UserProfile object
            
        Returns:
            MatchResult object
        """
        try:
            # Create text representations for embedding
            opportunity_text = self.cohere_service.create_opportunity_text(opportunity)
            profile_text = self.cohere_service.create_user_profile_text(profile)
            
            # Generate embeddings
            opportunity_embedding = self.cohere_service.get_embeddings([opportunity_text])[0]
            profile_embedding = self.cohere_service.get_embeddings([profile_text])[0]
            
            # Calculate semantic similarity
            semantic_similarity = self.cohere_service.calculate_similarity(
                opportunity_embedding, profile_embedding
            )
            
            # Calculate skill overlap
            matched_skills, skill_overlap = self.calculate_skill_overlap(
                profile.skills, opportunity.skills_required
            )
            
            # Calculate interest overlap
            matched_interests, interest_overlap = self.calculate_interest_overlap(
                profile.interests, opportunity_text
            )
            
            # Calculate weighted similarity score
            # 60% semantic similarity, 30% skill overlap, 10% interest overlap
            weighted_score = (
                0.6 * semantic_similarity +
                0.3 * skill_overlap +
                0.1 * interest_overlap
            )
            
            # Create match result
            match_result = MatchResult(
                opportunity=opportunity,
                user_profile=profile,
                similarity_score=weighted_score,
                matched_skills=matched_skills,
                matched_interests=matched_interests,
                reasoning=""
            )
            
            # Generate reasoning
            match_result.reasoning = self.generate_match_reasoning(match_result)
            
            return match_result
            
        except Exception as e:
            logger.error(f"Error matching opportunity {opportunity.id} with profile {profile.user_id}: {e}")
            # Return a low-score match result in case of error
            return MatchResult(
                opportunity=opportunity,
                user_profile=profile,
                similarity_score=0.0,
                matched_skills=[],
                matched_interests=[],
                reasoning="Error occurred during matching process."
            )
    
    def find_matches(self, opportunities: List[Opportunity], profile: UserProfile, 
                    min_score: float = None, max_results: int = 20) -> List[MatchResult]:
        """
        Find matching opportunities for a user profile.
        
        Args:
            opportunities: List of opportunities to match against
            profile: User profile to match with
            min_score: Minimum similarity score threshold
            max_results: Maximum number of results to return
            
        Returns:
            List of MatchResult objects, sorted by similarity score
        """
        if min_score is None:
            min_score = self.min_similarity_threshold
        
        logger.info(f"Finding matches for user {profile.user_id} from {len(opportunities)} opportunities")
        
        matches = []
        
        for opportunity in opportunities:
            match_result = self.match_opportunity_with_profile(opportunity, profile)
            
            # Only include matches above the threshold
            if match_result.similarity_score >= min_score:
                matches.append(match_result)
        
        # Sort by similarity score (descending)
        matches.sort(key=lambda x: x.similarity_score, reverse=True)
        
        # Limit results
        matches = matches[:max_results]
        
        logger.info(f"Found {len(matches)} matches above threshold {min_score}")
        return matches
    
    def find_matches_by_type(self, opportunities: List[Opportunity], profile: UserProfile,
                           opportunity_type: OpportunityType, min_score: float = None,
                           max_results: int = 10) -> List[MatchResult]:
        """
        Find matches for a specific type of opportunity.
        
        Args:
            opportunities: List of opportunities to match against
            profile: User profile to match with
            opportunity_type: Type of opportunities to filter for
            min_score: Minimum similarity score threshold
            max_results: Maximum number of results to return
            
        Returns:
            List of MatchResult objects for the specified type
        """
        # Filter opportunities by type
        filtered_opportunities = [
            opp for opp in opportunities 
            if opp.type == opportunity_type
        ]
        
        logger.info(f"Filtering {len(filtered_opportunities)} {opportunity_type.value} opportunities")
        
        return self.find_matches(filtered_opportunities, profile, min_score, max_results)
    
    def get_match_statistics(self, matches: List[MatchResult]) -> Dict[str, any]:
        """
        Get statistics about the matches.
        
        Args:
            matches: List of MatchResult objects
            
        Returns:
            Dictionary with match statistics
        """
        if not matches:
            return {
                "total_matches": 0,
                "average_score": 0.0,
                "highest_score": 0.0,
                "lowest_score": 0.0,
                "by_type": {},
                "by_source": {}
            }
        
        scores = [match.similarity_score for match in matches]
        
        # Count by type
        by_type = {}
        for match in matches:
            opp_type = match.opportunity.type.value
            by_type[opp_type] = by_type.get(opp_type, 0) + 1
        
        # Count by source
        by_source = {}
        for match in matches:
            source = match.opportunity.source
            by_source[source] = by_source.get(source, 0) + 1
        
        return {
            "total_matches": len(matches),
            "average_score": sum(scores) / len(scores),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "by_type": by_type,
            "by_source": by_source
        }
