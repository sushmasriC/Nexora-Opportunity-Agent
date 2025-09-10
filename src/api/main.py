"""
FastAPI main application for Nexora AI Agent.
Provides REST API endpoints for user management, authentication, and opportunity matching.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from ..agent import NexoraAgent
from ..database.user_db import UserDatabase
from ..services.auth_service import AuthService
from ..services.descope_verification import descope_verifier
from ..services.personalization_service import PersonalizationService
from ..services.weekly_email_service import WeeklyEmailService
from ..scheduler import SchedulerManager
from ..models import UserProfile, OpportunityType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Nexora AI Agent API",
    description="AI-powered opportunity matching and notification system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global instances (will be initialized in startup)
agent: Optional[NexoraAgent] = None
user_db: Optional[UserDatabase] = None
auth_service: Optional[AuthService] = None
personalization_service: Optional[PersonalizationService] = None
weekly_email_service: Optional[WeeklyEmailService] = None
scheduler_manager: Optional[SchedulerManager] = None


# Pydantic models for API
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    experience_level: Optional[str] = None
    preferred_locations: Optional[List[str]] = None
    remote_preference: Optional[bool] = None
    resume_text: Optional[str] = None


class UserPreferencesUpdate(BaseModel):
    notification_frequency: Optional[str] = "hourly"
    email_notifications: Optional[bool] = True
    min_match_score: Optional[float] = 0.3
    max_results: Optional[int] = 15
    preferred_sources: Optional[List[str]] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes


class UserResponse(BaseModel):
    id: str
    email: str
    created_at: str
    is_active: bool


class ProfileResponse(BaseModel):
    user_id: str
    skills: List[str]
    interests: List[str]
    experience_level: Optional[str]
    preferred_locations: List[str]
    remote_preference: bool
    resume_text: Optional[str]
    created_at: str
    updated_at: str


class MatchingRequest(BaseModel):
    user_id: str
    opportunity_types: Optional[List[str]] = None
    min_score: Optional[float] = 0.3
    max_results: Optional[int] = 15


class MatchingResponse(BaseModel):
    success: bool
    matches_found: int
    total_opportunities: int
    match_statistics: Dict[str, Any]
    duration_seconds: float
    timestamp: str


class OnboardingRequest(BaseModel):
    skills: List[str]
    interests: List[str]
    experience_level: Optional[str] = None
    preferred_locations: Optional[List[str]] = None
    remote_preference: Optional[bool] = True
    resume_text: Optional[str] = None
    notification_frequency: Optional[str] = "hourly"
    email_notifications: Optional[bool] = True
    min_match_score: Optional[float] = 0.3
    max_results: Optional[int] = 15
    preferred_sources: Optional[List[str]] = None


class OpportunityResponse(BaseModel):
    id: str
    title: str
    company: str
    location: str
    type: str
    source: str
    skills: List[str]
    description: str
    url: Optional[str] = None
    salary: Optional[str] = None
    deadline: Optional[str] = None

class RecommendationResponse(BaseModel):
    id: int
    opportunity_id: str
    opportunity_type: str
    similarity_score: float
    matched_skills: List[str]
    matched_interests: List[str]
    reasoning: str
    is_viewed: bool
    is_applied: bool
    created_at: str
    updated_at: str
    opportunity: OpportunityResponse


class SegregatedRecommendationsResponse(BaseModel):
    best_matches: List[RecommendationResponse]
    other_suggestions: List[RecommendationResponse]
    total_best_matches: int
    total_other_suggestions: int
    timestamp: str


# Dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from Descope session token."""
    token = credentials.credentials
    
    # Verify token with Descope
    payload = descope_verifier.verify_session_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user information from Descope token
    user_id = payload.get("sub") or payload.get("user_id")
    email = payload.get("email")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token - no user ID")
    
    # Return user info in expected format
    return {
        "user_id": user_id,
        "email": email,
        "sub": user_id,
        "descope_payload": payload
    }


async def get_user_db() -> UserDatabase:
    """Get user database instance."""
    if not user_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return user_db


async def get_agent() -> NexoraAgent:
    """Get Nexora agent instance."""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    return agent


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global agent, user_db, auth_service, personalization_service, weekly_email_service, scheduler_manager
    
    try:
        logger.info("Initializing Nexora AI Agent services...")
        
        # Initialize core services
        agent = NexoraAgent()
        user_db = UserDatabase()
        auth_service = AuthService()
        
        # Initialize personalization services
        personalization_service = PersonalizationService(agent.cohere_service, user_db)
        weekly_email_service = WeeklyEmailService(agent.email_service, personalization_service, user_db)
        
        # Initialize scheduler
        scheduler_manager = SchedulerManager()
        scheduler_manager.initialize(agent, user_db, personalization_service)
        scheduler_manager.start_scheduler()
        
        # Add weekly email job to scheduler
        scheduler_manager.scheduler.scheduler.add_job(
            func=weekly_email_service.send_weekly_summaries_to_all_users,
            trigger=weekly_email_service.get_weekly_summary_trigger(),
            id='weekly_summary_emails',
            name='Weekly Summary Emails',
            replace_existing=True
        )
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global scheduler_manager
    
    try:
        if scheduler_manager:
            scheduler_manager.stop_scheduler()
        logger.info("Services shutdown successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# Authentication endpoints
@app.post("/auth/register", response_model=TokenResponse)
async def register_user(
    user_data: UserRegistration,
    db: UserDatabase = Depends(get_user_db)
):
    """Register a new user."""
    try:
        # Check if user already exists
        existing_user = db.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Register with auth service
        success, message, access_token = auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            user_data={
                "first_name": user_data.first_name,
                "last_name": user_data.last_name
            }
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Create user in database
        user_id = f"user_{hash(user_data.email) % 100000}"
        db.create_user(user_id, user_data.email)
        
        return TokenResponse(access_token=access_token)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/auth/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    db: UserDatabase = Depends(get_user_db)
):
    """Login user."""
    try:
        success, message, access_token = auth_service.authenticate_user(
            email=login_data.email,
            password=login_data.password
        )
        
        if not success:
            raise HTTPException(status_code=401, detail=message)
        
        return TokenResponse(access_token=access_token)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# User management endpoints
@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: UserDatabase = Depends(get_user_db)
):
    """Get current user information."""
    try:
        user_id = current_user["user_id"]
        user = db.get_user(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=user["id"],
            email=user["email"],
            created_at=user["created_at"],
            is_active=user["is_active"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/users/me/profile", response_model=ProfileResponse)
async def get_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: UserDatabase = Depends(get_user_db)
):
    """Get user profile."""
    try:
        user_id = current_user["user_id"]
        profile = db.get_user_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return ProfileResponse(
            user_id=profile.user_id,
            skills=profile.skills,
            interests=profile.interests,
            experience_level=profile.experience_level,
            preferred_locations=profile.preferred_locations,
            remote_preference=profile.remote_preference,
            resume_text=profile.resume_text,
            created_at=profile.created_at.isoformat(),
            updated_at=profile.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/users/me/profile", response_model=ProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: UserDatabase = Depends(get_user_db)
):
    """Update user profile."""
    try:
        user_id = current_user["user_id"]
        
        # Get existing profile
        existing_profile = db.get_user_profile(user_id)
        if not existing_profile:
            # Create new profile
            existing_profile = UserProfile(
                user_id=user_id,
                email=current_user["email"]
            )
        
        # Update fields
        if profile_update.skills is not None:
            existing_profile.skills = profile_update.skills
        if profile_update.interests is not None:
            existing_profile.interests = profile_update.interests
        if profile_update.experience_level is not None:
            existing_profile.experience_level = profile_update.experience_level
        if profile_update.preferred_locations is not None:
            existing_profile.preferred_locations = profile_update.preferred_locations
        if profile_update.remote_preference is not None:
            existing_profile.remote_preference = profile_update.remote_preference
        if profile_update.resume_text is not None:
            existing_profile.resume_text = profile_update.resume_text
        
        # Save profile
        success = db.create_user_profile(existing_profile)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        
        return ProfileResponse(
            user_id=existing_profile.user_id,
            skills=existing_profile.skills,
            interests=existing_profile.interests,
            experience_level=existing_profile.experience_level,
            preferred_locations=existing_profile.preferred_locations,
            remote_preference=existing_profile.remote_preference,
            resume_text=existing_profile.resume_text,
            created_at=existing_profile.created_at.isoformat(),
            updated_at=existing_profile.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/users/me/preferences")
async def get_user_preferences(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: UserDatabase = Depends(get_user_db)
):
    """Get user preferences."""
    try:
        user_id = current_user["user_id"]
        preferences = db.get_user_preferences(user_id)
        
        if not preferences:
            # Return default preferences
            preferences = {
                "notification_frequency": "hourly",
                "email_notifications": True,
                "min_match_score": 0.3,
                "max_results": 15,
                "preferred_sources": []
            }
        
        return preferences
        
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/users/me/preferences")
async def update_user_preferences(
    preferences_update: UserPreferencesUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: UserDatabase = Depends(get_user_db)
):
    """Update user preferences."""
    try:
        user_id = current_user["user_id"]
        
        # Convert to dict and filter None values
        update_data = {
            k: v for k, v in preferences_update.dict().items() 
            if v is not None
        }
        
        success = db.update_user_preferences(user_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update preferences")
        
        return {"message": "Preferences updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Opportunity matching endpoints
@app.post("/matching/run", response_model=MatchingResponse)
async def run_matching(
    matching_request: MatchingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    agent: NexoraAgent = Depends(get_agent),
    db: UserDatabase = Depends(get_user_db)
):
    """Run immediate opportunity matching for a user."""
    try:
        user_id = current_user["user_id"]
        
        # Get user profile
        profile = db.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get user data for email
        user_data = db.get_user(user_id)
        if user_data:
            profile.email = user_data["email"]
        
        # Run matching workflow
        result = agent.run_full_workflow(
            user_profile=profile,
            limit_per_source=10,
            min_score=matching_request.min_score or 0.3,
            max_results=matching_request.max_results or 15
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Matching failed"))
        
        return MatchingResponse(
            success=result["success"],
            matches_found=result["matches_found"],
            total_opportunities=result["total_opportunities"],
            match_statistics=result["match_statistics"],
            duration_seconds=result["duration_seconds"],
            timestamp=result["timestamp"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running matching: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/opportunities")
async def get_opportunities(
    opportunity_type: Optional[str] = None,
    limit: int = 20,
    agent: NexoraAgent = Depends(get_agent)
):
    """Get opportunities from all sources."""
    try:
        if opportunity_type:
            try:
                opp_type = OpportunityType(opportunity_type)
                opportunities = agent.get_opportunities_by_type(opp_type, limit)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid opportunity type")
        else:
            opportunities = agent.fetch_opportunities(limit_per_source=limit//4)
        
        # Convert to dict format for JSON response
        opportunities_data = []
        for opp in opportunities:
            opportunities_data.append({
                "id": opp.id,
                "title": opp.title,
                "company": opp.company,
                "description": opp.description,
                "location": opp.location,
                "type": opp.type.value,
                "url": opp.url,
                "posted_date": opp.posted_date.isoformat() if opp.posted_date else None,
                "deadline": opp.deadline.isoformat() if opp.deadline else None,
                "skills_required": opp.skills_required,
                "salary_range": opp.salary_range,
                "experience_level": opp.experience_level,
                "remote": opp.remote,
                "source": opp.source
            })
        
        return {
            "opportunities": opportunities_data,
            "total_count": len(opportunities_data),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Scheduler management endpoints
@app.get("/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status."""
    try:
        if not scheduler_manager:
            raise HTTPException(status_code=500, detail="Scheduler not initialized")
        
        status_info = scheduler_manager.get_status()
        return status_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/scheduler/run-immediate")
async def run_immediate_matching(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Run immediate matching for current user."""
    try:
        if not scheduler_manager:
            raise HTTPException(status_code=500, detail="Scheduler not initialized")
        
        user_id = current_user["user_id"]
        result = scheduler_manager.run_immediate_matching(user_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running immediate matching: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Admin endpoints
# User onboarding endpoints
@app.post("/users/onboarding")
async def complete_user_onboarding(
    onboarding_data: OnboardingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: UserDatabase = Depends(get_user_db)
):
    """Complete user onboarding with skills, interests, and preferences."""
    try:
        user_id = current_user["user_id"]
        
        # Get user email
        user_data = db.get_user(user_id)
        if user_data:
            onboarding_data.email = user_data["email"]
        
        # Process onboarding
        success = personalization_service.process_user_onboarding(user_id, onboarding_data.dict())
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to process onboarding")
        
        return {"message": "Onboarding completed successfully", "user_id": user_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing onboarding: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/users/me/recommendations", response_model=SegregatedRecommendationsResponse)
async def get_segregated_recommendations(
    limit: int = 20,
    # Temporarily remove authentication for testing
    # current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get segregated recommendations (best matches vs other suggestions)."""
    try:
        logger.info("Starting recommendations endpoint")
        # For testing, use a mock user_id
        user_id = "test_user_123"
        
        # Return mock data for testing
        mock_recommendations = {
            "best_matches": [
                {
                    "id": 1,
                    "opportunity_id": "opp_1",
                    "opportunity_type": "job",
                    "similarity_score": 0.95,
                    "matched_skills": ["Python", "React", "Machine Learning"],
                    "matched_interests": ["AI", "Web Development"],
                    "reasoning": "High match based on your Python and React skills",
                    "is_viewed": False,
                    "is_applied": False,
                    "created_at": "2025-01-08T10:00:00Z",
                    "updated_at": "2025-01-08T10:00:00Z",
                    "opportunity": {
                        "id": "opp_1",
                        "title": "Senior Python Developer",
                        "company": "TechCorp Inc",
                        "location": "Bangalore, India",
                        "type": "job",
                        "source": "indeed",
                        "skills": ["Python", "React", "Machine Learning", "Docker"],
                        "description": "Join our team as a Senior Python Developer working on cutting-edge AI projects.",
                        "url": "https://example.com/job/1",
                        "salary": "$120,000 - $150,000",
                        "deadline": "2025-02-15"
                    }
                },
                {
                    "id": 2, 
                    "opportunity_id": "opp_2",
                    "opportunity_type": "hackathon",
                    "similarity_score": 0.88,
                    "matched_skills": ["JavaScript", "Node.js"],
                    "matched_interests": ["Full Stack Development"],
                    "reasoning": "Great match for your full-stack development interests",
                    "is_viewed": False,
                    "is_applied": False,
                    "created_at": "2025-01-08T09:30:00Z",
                    "updated_at": "2025-01-08T09:30:00Z",
                    "opportunity": {
                        "id": "opp_2",
                        "title": "AI Innovation Hackathon",
                        "company": "Hackathon Corp",
                        "location": "Remote",
                        "type": "hackathon",
                        "source": "devpost",
                        "skills": ["JavaScript", "Node.js", "AI", "Machine Learning"],
                        "description": "Build innovative AI solutions in this 48-hour hackathon.",
                        "url": "https://example.com/hackathon/1",
                        "deadline": "2025-01-20"
                    }
                }
            ],
            "other_suggestions": [
                {
                    "id": 3,
                    "opportunity_id": "opp_3", 
                    "opportunity_type": "job",
                    "similarity_score": 0.65,
                    "matched_skills": ["Python"],
                    "matched_interests": ["Data Science"],
                    "reasoning": "Good match for your Python skills",
                    "is_viewed": False,
                    "is_applied": False,
                    "created_at": "2025-01-08T09:00:00Z",
                    "updated_at": "2025-01-08T09:00:00Z",
                    "opportunity": {
                        "id": "opp_3",
                        "title": "Data Scientist",
                        "company": "DataCorp",
                        "location": "Hyderabad, India",
                        "type": "job",
                        "source": "linkedin",
                        "skills": ["Python", "Data Science", "Machine Learning", "SQL"],
                        "description": "Work with large datasets to extract meaningful insights.",
                        "url": "https://example.com/job/2",
                        "salary": "$100,000 - $130,000",
                        "deadline": "2025-02-01"
                    }
                }
            ],
            "total_best_matches": 2,
            "total_other_suggestions": 1,
            "timestamp": "2025-01-08T10:00:00Z"
        }
        
        recommendations = mock_recommendations
        
        if "error" in recommendations:
            raise HTTPException(status_code=500, detail=recommendations["error"])
        
        # Convert to response models
        logger.info("Converting to response models")
        try:
            best_matches = [
                RecommendationResponse(**rec) for rec in recommendations["best_matches"]
            ]
            logger.info(f"Created {len(best_matches)} best matches")
        except Exception as e:
            logger.error(f"Error creating best_matches: {e}")
            raise
        
        try:
            other_suggestions = [
                RecommendationResponse(**rec) for rec in recommendations["other_suggestions"]
            ]
            logger.info(f"Created {len(other_suggestions)} other suggestions")
        except Exception as e:
            logger.error(f"Error creating other_suggestions: {e}")
            raise
        
        try:
            response = SegregatedRecommendationsResponse(
                best_matches=best_matches,
                other_suggestions=other_suggestions,
                total_best_matches=recommendations["total_best_matches"],
                total_other_suggestions=recommendations["total_other_suggestions"],
                timestamp=recommendations["timestamp"]
            )
            logger.info("Successfully created response")
            return response
        except Exception as e:
            logger.error(f"Error creating final response: {e}")
            raise
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting segregated recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/users/me/recommendations/{recommendation_id}/view")
async def mark_recommendation_viewed(
    recommendation_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Mark a recommendation as viewed."""
    try:
        user_id = current_user["user_id"]
        
        # Get recommendation to verify ownership
        recommendations = user_db.get_user_recommendations(user_id, limit=1000)
        recommendation = next(
            (rec for rec in recommendations if rec['id'] == recommendation_id), 
            None
        )
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        success = user_db.mark_recommendation_viewed(recommendation_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to mark as viewed")
        
        return {"message": "Recommendation marked as viewed"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking recommendation as viewed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/users/me/recommendations/{recommendation_id}/apply")
async def mark_recommendation_applied(
    recommendation_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Mark a recommendation as applied."""
    try:
        user_id = current_user["user_id"]
        
        # Get recommendation to verify ownership
        recommendations = user_db.get_user_recommendations(user_id, limit=1000)
        recommendation = next(
            (rec for rec in recommendations if rec['id'] == recommendation_id), 
            None
        )
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        success = user_db.mark_recommendation_applied(recommendation_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to mark as applied")
        
        return {"message": "Recommendation marked as applied"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking recommendation as applied: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/users/me/analytics")
async def get_user_analytics(
    # Temporarily remove authentication for testing
    # current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user analytics and insights."""
    try:
        # Return mock analytics data for testing
        mock_analytics = {
            "total_recommendations": 15,
            "viewed_recommendations": 8,
            "applied_recommendations": 3,
            "top_skills": ["Python", "React", "JavaScript", "Machine Learning"],
            "top_interests": ["AI", "Web Development", "Data Science"],
            "match_score_avg": 0.78,
            "last_updated": "2025-01-08T10:00:00Z"
        }
        
        return mock_analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/users/me/resume/upload")
async def upload_resume(
    file_path: str,
    file_name: str,
    file_size: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: UserDatabase = Depends(get_user_db)
):
    """Upload resume file."""
    try:
        user_id = current_user["user_id"]
        
        success = db.upload_resume(user_id, file_path, file_name, file_size)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to upload resume")
        
        return {"message": "Resume uploaded successfully", "file_name": file_name}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/users/me/resumes")
async def get_user_resumes(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: UserDatabase = Depends(get_user_db)
):
    """Get user's uploaded resumes."""
    try:
        user_id = current_user["user_id"]
        
        resumes = db.get_user_resumes(user_id)
        
        return {
            "resumes": resumes,
            "total_count": len(resumes),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting user resumes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Weekly email endpoints
@app.post("/admin/send-weekly-summaries")
async def send_weekly_summaries(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Send weekly summary emails to all users (admin only)."""
    try:
        # In a real implementation, you'd check if user is admin
        
        result = weekly_email_service.send_weekly_summaries_to_all_users()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending weekly summaries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/admin/users")
async def get_all_users(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: UserDatabase = Depends(get_user_db)
):
    """Get all users (admin only)."""
    try:
        # In a real implementation, you'd check if user is admin
        users = db.get_all_users()
        
        return {
            "users": users,
            "total_count": len(users),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
