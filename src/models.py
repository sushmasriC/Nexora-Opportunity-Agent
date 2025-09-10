"""
Data models for Nexora AI Agent.
Defines the structure for opportunities, user profiles, and matching results.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class OpportunityType(str, Enum):
    """Types of opportunities available."""
    JOB = "job"
    INTERNSHIP = "internship"
    HACKATHON = "hackathon"


class Opportunity(BaseModel):
    """Represents a job, internship, or hackathon opportunity."""
    
    id: str
    title: str
    company: str
    description: str
    location: Optional[str] = None
    type: OpportunityType
    url: str
    posted_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    skills_required: List[str] = Field(default_factory=list)
    salary_range: Optional[str] = None
    experience_level: Optional[str] = None
    remote: bool = False
    source: str  # e.g., "wellfound", "internshala", "unstop"
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class UserProfile(BaseModel):
    """User profile containing skills, interests, and preferences."""
    
    user_id: str
    email: str
    skills: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    experience_level: Optional[str] = None
    preferred_locations: List[str] = Field(default_factory=list)
    remote_preference: bool = True
    resume_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class MatchResult(BaseModel):
    """Result of matching an opportunity with a user profile."""
    
    opportunity: Opportunity
    user_profile: UserProfile
    similarity_score: float = Field(ge=0.0, le=1.0)
    matched_skills: List[str] = Field(default_factory=list)
    matched_interests: List[str] = Field(default_factory=list)
    reasoning: str = ""


class EmailNotification(BaseModel):
    """Email notification to be sent to user."""
    
    to_email: str
    subject: str
    opportunities: List[MatchResult]
    total_matches: int
    sent_at: Optional[datetime] = None
