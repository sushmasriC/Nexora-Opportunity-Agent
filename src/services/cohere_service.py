"""
Cohere service for embeddings and text similarity.
Handles text embeddings generation and similarity calculations.
"""

import cohere
from typing import List, Dict, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

from ..config import settings
from ..models import Opportunity, UserProfile

logger = logging.getLogger(__name__)


class CohereService:
    """Service for handling Cohere API operations."""
    
    def __init__(self):
        """Initialize Cohere client."""
        self.client = cohere.Client(settings.cohere_api_key)
        self.model = "embed-english-v3.0"
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embed(
                texts=texts,
                model=self.model,
                input_type="search_document"
            )
            return response.embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def get_query_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a query text.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = self.client.embed(
                texts=[text],
                model=self.model,
                input_type="search_query"
            )
            return response.embeddings[0]
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Convert to numpy arrays and reshape for cosine_similarity
            emb1 = np.array(embedding1).reshape(1, -1)
            emb2 = np.array(embedding2).reshape(1, -1)
            
            similarity = cosine_similarity(emb1, emb2)[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def create_opportunity_text(self, opportunity: Opportunity) -> str:
        """
        Create a text representation of an opportunity for embedding.
        
        Args:
            opportunity: Opportunity object
            
        Returns:
            Text representation of the opportunity
        """
        text_parts = [
            f"Title: {opportunity.title}",
            f"Company: {opportunity.company}",
            f"Description: {opportunity.description}",
            f"Type: {opportunity.type.value}",
        ]
        
        if opportunity.location:
            text_parts.append(f"Location: {opportunity.location}")
        
        if opportunity.skills_required:
            text_parts.append(f"Skills: {', '.join(opportunity.skills_required)}")
        
        if opportunity.experience_level:
            text_parts.append(f"Experience: {opportunity.experience_level}")
        
        if opportunity.salary_range:
            text_parts.append(f"Salary: {opportunity.salary_range}")
        
        return " | ".join(text_parts)
    
    def create_user_profile_text(self, profile: UserProfile) -> str:
        """
        Create a text representation of a user profile for embedding.
        
        Args:
            profile: UserProfile object
            
        Returns:
            Text representation of the user profile
        """
        text_parts = []
        
        if profile.skills:
            text_parts.append(f"Skills: {', '.join(profile.skills)}")
        
        if profile.interests:
            text_parts.append(f"Interests: {', '.join(profile.interests)}")
        
        if profile.experience_level:
            text_parts.append(f"Experience Level: {profile.experience_level}")
        
        if profile.preferred_locations:
            text_parts.append(f"Preferred Locations: {', '.join(profile.preferred_locations)}")
        
        if profile.resume_text:
            text_parts.append(f"Resume: {profile.resume_text[:500]}...")  # Truncate for embedding
        
        return " | ".join(text_parts)
