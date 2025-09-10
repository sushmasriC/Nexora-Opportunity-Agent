"""
Opportunity fetchers for different platforms.
Now uses web scraping instead of APIs and mock data.
"""

import requests
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

from ..models import Opportunity, OpportunityType
from ..config import settings
from .web_scraping_fetchers import get_web_scraping_fetcher
from .apify_fetchers import (
    WellfoundApifyFetcher, 
    GreenhouseApifyFetcher, 
    IndeedRapidAPIFetcher, 
    LinkedInApifyFetcher
)
from .hackathon_fetchers import (
    EventbriteHackathonFetcher,
    HackerEarthHackathonFetcher
)

logger = logging.getLogger(__name__)


class BaseOpportunityFetcher:
    """Base class for opportunity fetchers."""
    
    def __init__(self, api_key: str = None):
        """Initialize the fetcher with API key."""
        self.api_key = api_key
        self.base_url = ""
    
    def fetch_opportunities(self, **kwargs) -> List[Opportunity]:
        """
        Fetch opportunities from the platform.
        
        Args:
            **kwargs: Additional parameters for fetching
            
        Returns:
            List of Opportunity objects
        """
        raise NotImplementedError("Subclasses must implement fetch_opportunities")


class WellfoundFetcher(BaseOpportunityFetcher):
    """Fetcher for Wellfound (AngelList) job opportunities."""
    
    def __init__(self, api_key: str = None):
        """Initialize Wellfound fetcher."""
        super().__init__(api_key or settings.wellfound_api_key)
        self.base_url = "https://api.wellfound.com"
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch job opportunities from Wellfound.
        
        Args:
            limit: Maximum number of opportunities to fetch
            
        Returns:
            List of Opportunity objects
        """
        # Placeholder implementation - returns sample data
        logger.info(f"Fetching {limit} opportunities from Wellfound")
        
        sample_jobs = [
            {
                "id": f"wellfound_job_{i}",
                "title": f"Senior Software Engineer - {['Python', 'React', 'Node.js', 'AI/ML'][i % 4]}",
                "company": f"Tech Company {i + 1}",
                "description": f"Join our innovative team working on cutting-edge {['web applications', 'AI solutions', 'mobile apps', 'data platforms'][i % 4]}. We're looking for passionate developers who want to make an impact.",
                "location": random.choice(["Bangalore, India", "Hyderabad, India", "Remote", "Mumbai, India", "Delhi, India"]),
                "skills": random.sample(["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes", "Machine Learning", "Data Science"], 3),
                "salary": f"${random.randint(80, 200)}k - ${random.randint(200, 400)}k",
                "experience": random.choice(["Mid-level", "Senior", "Lead"]),
                "url": f"https://wellfound.com/company/tech-company-{i + 1}/jobs/{i + 1}"
            }
            for i in range(min(limit, 20))
        ]
        
        opportunities = []
        for job_data in sample_jobs:
            opportunity = Opportunity(
                id=job_data["id"],
                title=job_data["title"],
                company=job_data["company"],
                description=job_data["description"],
                location=job_data["location"],
                type=OpportunityType.JOB,
                url=job_data["url"],
                posted_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                skills_required=job_data["skills"],
                salary_range=job_data["salary"],
                experience_level=job_data["experience"],
                remote=job_data["location"] == "Remote",
                source="wellfound",
                raw_data=job_data
            )
            opportunities.append(opportunity)
        
        logger.info(f"Fetched {len(opportunities)} opportunities from Wellfound")
        return opportunities


class InternshalaFetcher(BaseOpportunityFetcher):
    """Fetcher for Internshala internship opportunities."""
    
    def __init__(self, api_key: str = None):
        """Initialize Internshala fetcher."""
        super().__init__(api_key or settings.internshala_api_key)
        self.base_url = "https://internshala.com/api"
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch internship opportunities from Internshala.
        
        Args:
            limit: Maximum number of opportunities to fetch
            
        Returns:
            List of Opportunity objects
        """
        # Placeholder implementation - returns sample data
        logger.info(f"Fetching {limit} internships from Internshala")
        
        sample_internships = [
            {
                "id": f"internshala_intern_{i}",
                "title": f"{['Software Development', 'Data Science', 'Marketing', 'Design', 'Content Writing'][i % 5]} Intern",
                "company": f"Startup {i + 1}",
                "description": f"Exciting internship opportunity in {['software development', 'data analysis', 'digital marketing', 'UI/UX design', 'content creation'][i % 5]}. Perfect for students and recent graduates looking to gain real-world experience.",
                "location": random.choice(["Mumbai", "Bangalore", "Delhi", "Remote", "Pune"]),
                "skills": random.sample(["Python", "Java", "Marketing", "Design", "Writing", "Analytics", "Social Media", "Photoshop"], 2),
                "duration": f"{random.randint(2, 6)} months",
                "stipend": f"₹{random.randint(5, 25)}k/month",
                "url": f"https://internshala.com/internship/detail/startup-{i + 1}-{i + 1}"
            }
            for i in range(min(limit, 15))
        ]
        
        opportunities = []
        for intern_data in sample_internships:
            opportunity = Opportunity(
                id=intern_data["id"],
                title=intern_data["title"],
                company=intern_data["company"],
                description=intern_data["description"],
                location=intern_data["location"],
                type=OpportunityType.INTERNSHIP,
                url=intern_data["url"],
                posted_date=datetime.now() - timedelta(days=random.randint(1, 15)),
                deadline=datetime.now() + timedelta(days=random.randint(7, 30)),
                skills_required=intern_data["skills"],
                salary_range=intern_data["stipend"],
                experience_level="Entry-level",
                remote=intern_data["location"] == "Remote",
                source="internshala",
                raw_data=intern_data
            )
            opportunities.append(opportunity)
        
        logger.info(f"Fetched {len(opportunities)} internships from Internshala")
        return opportunities


class UnstopFetcher(BaseOpportunityFetcher):
    """Fetcher for Unstop hackathon opportunities."""
    
    def __init__(self, api_key: str = None):
        """Initialize Unstop fetcher."""
        super().__init__(api_key or settings.unstop_api_key)
        self.base_url = "https://unstop.com/api"
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch hackathon opportunities from Unstop.
        
        Args:
            limit: Maximum number of opportunities to fetch
            
        Returns:
            List of Opportunity objects
        """
        # Placeholder implementation - returns sample data
        logger.info(f"Fetching {limit} hackathons from Unstop")
        
        sample_hackathons = [
            {
                "id": f"unstop_hack_{i}",
                "title": f"{['AI Innovation', 'Web3 Challenge', 'FinTech', 'EdTech', 'HealthTech'][i % 5]} Hackathon",
                "company": f"Hackathon Organizer {i + 1}",
                "description": f"Join our {['AI Innovation', 'Web3', 'FinTech', 'EdTech', 'HealthTech'][i % 5]} hackathon and build innovative solutions. Prizes worth ₹{random.randint(50, 500)}k up for grabs!",
                "location": random.choice(["Online", "Bangalore", "Mumbai", "Delhi", "Hyderabad"]),
                "skills": random.sample(["Programming", "AI/ML", "Blockchain", "Design", "Presentation", "Teamwork"], 3),
                "prize": f"₹{random.randint(50, 500)}k",
                "duration": f"{random.randint(24, 72)} hours",
                "url": f"https://unstop.com/hackathon/ai-innovation-{i + 1}"
            }
            for i in range(min(limit, 10))
        ]
        
        opportunities = []
        for hack_data in sample_hackathons:
            opportunity = Opportunity(
                id=hack_data["id"],
                title=hack_data["title"],
                company=hack_data["company"],
                description=hack_data["description"],
                location=hack_data["location"],
                type=OpportunityType.HACKATHON,
                url=hack_data["url"],
                posted_date=datetime.now() - timedelta(days=random.randint(1, 10)),
                deadline=datetime.now() + timedelta(days=random.randint(3, 21)),
                skills_required=hack_data["skills"],
                salary_range=hack_data["prize"],
                experience_level="Any",
                remote=hack_data["location"] == "Online",
                source="unstop",
                raw_data=hack_data
            )
            opportunities.append(opportunity)
        
        logger.info(f"Fetched {len(opportunities)} hackathons from Unstop")
        return opportunities


class OpportunityFetcherManager:
    """Manager class to coordinate fetching from multiple sources."""
    
    def __init__(self):
        """Initialize the manager with web scraping fetcher."""
        self.web_scraping_fetcher = get_web_scraping_fetcher()
        # Keep legacy fetchers for fallback
        self.legacy_fetchers = {
            # Job fetchers
            "wellfound": WellfoundApifyFetcher(),
            "greenhouse": GreenhouseApifyFetcher(),
            "indeed": IndeedRapidAPIFetcher(),
            "linkedin": LinkedInApifyFetcher(),
            # Hackathon fetchers
            "eventbrite": EventbriteHackathonFetcher(),
            "hackerearth": HackerEarthHackathonFetcher(),
            # Legacy fetchers for backward compatibility
            "internshala": InternshalaFetcher(),
            "unstop": UnstopFetcher()
        }
    
    def fetch_all_opportunities(self, limit_per_source: int = 20) -> List[Opportunity]:
        """
        Fetch opportunities from all sources using web scraping.
        
        Args:
            limit_per_source: Maximum opportunities to fetch from each source
            
        Returns:
            Combined list of all opportunities
        """
        try:
            # Try web scraping first
            if settings.web_scraping_enabled:
                logger.info("Using web scraping to fetch opportunities")
                return self.web_scraping_fetcher.fetch_all_opportunities(limit_per_source)
            else:
                logger.info("Web scraping disabled, using legacy fetchers")
                return self._fetch_with_legacy_fetchers(limit_per_source)
        except Exception as e:
            logger.error(f"Error with web scraping, falling back to legacy fetchers: {e}")
            return self._fetch_with_legacy_fetchers(limit_per_source)
    
    def fetch_opportunities_by_type(self, opportunity_type: OpportunityType, limit: int = 30) -> List[Opportunity]:
        """
        Fetch opportunities of a specific type using web scraping.
        
        Args:
            opportunity_type: Type of opportunities to fetch
            limit: Maximum number of opportunities to fetch
            
        Returns:
            List of opportunities of the specified type
        """
        try:
            # Try web scraping first
            if settings.web_scraping_enabled:
                logger.info(f"Using web scraping to fetch {opportunity_type.value} opportunities")
                return self.web_scraping_fetcher.fetch_opportunities_by_type(opportunity_type, limit)
            else:
                logger.info("Web scraping disabled, using legacy fetchers")
                return self._fetch_by_type_with_legacy_fetchers(opportunity_type, limit)
        except Exception as e:
            logger.error(f"Error with web scraping, falling back to legacy fetchers: {e}")
            return self._fetch_by_type_with_legacy_fetchers(opportunity_type, limit)
    
    def _fetch_with_legacy_fetchers(self, limit_per_source: int) -> List[Opportunity]:
        """Fallback method using legacy fetchers."""
        all_opportunities = []
        
        for source_name, fetcher in self.legacy_fetchers.items():
            try:
                opportunities = fetcher.fetch_opportunities(limit=limit_per_source)
                all_opportunities.extend(opportunities)
                logger.info(f"Successfully fetched {len(opportunities)} opportunities from {source_name}")
            except Exception as e:
                logger.error(f"Error fetching opportunities from {source_name}: {e}")
        
        logger.info(f"Total opportunities fetched: {len(all_opportunities)}")
        return all_opportunities
    
    def _fetch_by_type_with_legacy_fetchers(self, opportunity_type: OpportunityType, limit: int) -> List[Opportunity]:
        """Fallback method for fetching by type using legacy fetchers."""
        opportunities = []
        
        if opportunity_type == OpportunityType.JOB:
            # Fetch from all job sources
            job_sources = ["wellfound", "greenhouse", "indeed", "linkedin"]
            limit_per_source = limit // len(job_sources)
            
            for source in job_sources:
                try:
                    source_opportunities = self.legacy_fetchers[source].fetch_opportunities(limit=limit_per_source)
                    opportunities.extend(source_opportunities)
                except Exception as e:
                    logger.error(f"Error fetching from {source}: {e}")
                    continue
                    
        elif opportunity_type == OpportunityType.INTERNSHIP:
            opportunities.extend(self.legacy_fetchers["internshala"].fetch_opportunities(limit=limit))
        elif opportunity_type == OpportunityType.HACKATHON:
            # Fetch from all hackathon sources
            hackathon_sources = ["eventbrite", "hackerearth", "unstop"]
            limit_per_source = limit // len(hackathon_sources)
            
            for source in hackathon_sources:
                try:
                    source_opportunities = self.legacy_fetchers[source].fetch_opportunities(limit=limit_per_source)
                    opportunities.extend(source_opportunities)
                except Exception as e:
                    logger.error(f"Error fetching from {source}: {e}")
                    continue
        
        return opportunities
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            if hasattr(self.web_scraping_fetcher, 'cleanup'):
                self.web_scraping_fetcher.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Cleanup on deletion."""
        self.cleanup()
