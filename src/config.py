"""
Configuration management for Nexora AI Agent.
Handles loading environment variables and API keys.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Redis Configuration
    redis_url: Optional[str] = Field(None, env="REDIS_URL")
    
    # AI/ML APIs
    cohere_api_key: str = Field(..., env="COHERE_API_KEY")
    
    # Authentication
    descope_project_id: Optional[str] = Field(None, env="DESCOPE_PROJECT_ID")
    descope_api_key: Optional[str] = Field(None, env="DESCOPE_API_KEY")
    
    # Email Configuration
    sendgrid_api_key: str = Field(..., env="SENDGRID_API_KEY")
    email_sender: str = Field(..., env="EMAIL_SENDER")
    email_password: Optional[str] = Field(None, env="EMAIL_PASSWORD")
    
    # Job Board APIs - Wellfound (Apify)
    wellfound_api_token: Optional[str] = Field(None, env="WELLFOUND_API_TOKEN")
    wellfound_actor_id: Optional[str] = Field(None, env="WELLFOUND_ACTOR_ID")
    wellfound_start_url: str = Field("https://wellfound.com/jobs", env="WELLFOUND_START_URL")
    
    # Job Board APIs - Greenhouse (Apify)
    greenhouse_api_token: Optional[str] = Field(None, env="GREENHOUSE_API_TOKEN")
    greenhouse_actor_id: Optional[str] = Field(None, env="GREENHOUSE_ACTOR_ID")
    greenhouse_start_url: str = Field("https://boards.greenhouse.io/company/jobs", env="GREENHOUSE_START_URL")
    
    # Job Board APIs - Indeed (RapidAPI & Apify)
    indeed_api_key: Optional[str] = Field(None, env="INDEED_API_KEY")
    indeed_api_token: Optional[str] = Field(None, env="INDEED_API_TOKEN")
    indeed_actor_id: Optional[str] = Field(None, env="INDEED_ACTOR_ID")
    indeed_start_url: str = Field("https://indeed.com/jobs", env="INDEED_START_URL")
    
    # Job Board APIs - LinkedIn (Apify)
    linkedin_api_token: Optional[str] = Field(None, env="LINKEDIN_API_TOKEN")
    linkedin_actor_id: Optional[str] = Field(None, env="LINKEDIN_ACTOR_ID")
    linkedin_start_url: str = Field("https://linkedin.com/jobs", env="LINKEDIN_START_URL")
    
    # Hackathon APIs - Eventbrite (Apify)
    eventbrite_api_token: Optional[str] = Field(None, env="EVENTBRITE_API_TOKEN")
    eventbrite_actor_id: Optional[str] = Field(None, env="EVENTBRITE_ACTOR_ID")
    eventbrite_start_url: str = Field("https://www.eventbrite.com/d/online/hackathon/", env="EVENTBRITE_START_URL")
    
    # Hackathon APIs - HackerEarth (RapidAPI)
    hackerearth_api_url: str = Field("https://ideas2it-hackerearth.p.rapidapi.com/run/", env="HACKEREARTH_API_URL")
    hackerearth_api_key: Optional[str] = Field(None, env="HACKEREARTH_API_KEY")
    
    # Legacy API Keys (for backward compatibility)
    wellfound_api_key: Optional[str] = Field(None, env="WELLFOUND_API_KEY")
    internshala_api_key: Optional[str] = Field(None, env="INTERNSHALA_API_KEY")
    unstop_api_key: Optional[str] = Field(None, env="UNSTOP_API_KEY")
    
    # Web Scraping Configuration
    web_scraping_enabled: bool = Field(True, env="WEB_SCRAPING_ENABLED")
    web_scraping_delay_min: float = Field(1.0, env="WEB_SCRAPING_DELAY_MIN")
    web_scraping_delay_max: float = Field(3.0, env="WEB_SCRAPING_DELAY_MAX")
    web_scraping_timeout: int = Field(30, env="WEB_SCRAPING_TIMEOUT")
    web_scraping_max_retries: int = Field(3, env="WEB_SCRAPING_MAX_RETRIES")
    web_scraping_user_agent: Optional[str] = Field(None, env="WEB_SCRAPING_USER_AGENT")
    web_scraping_proxy: Optional[str] = Field(None, env="WEB_SCRAPING_PROXY")
    
    # Selenium Configuration
    selenium_headless: bool = Field(True, env="SELENIUM_HEADLESS")
    selenium_window_size: str = Field("1920,1080", env="SELENIUM_WINDOW_SIZE")
    selenium_driver_path: Optional[str] = Field(None, env="SELENIUM_DRIVER_PATH")
    
    # Backward compatibility properties
    @property
    def from_email(self) -> str:
        return self.email_sender
    
    @property
    def from_name(self) -> str:
        return "Nexora AI Agent"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_settings() -> Settings:
    """Load settings from environment variables."""
    load_dotenv()
    return Settings()


# Global settings instance
settings = load_settings()
