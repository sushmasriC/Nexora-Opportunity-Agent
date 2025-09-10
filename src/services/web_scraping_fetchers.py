"""
Web scraping-based opportunity fetchers.
Replaces API-based and mock data fetchers with real web scraping.
"""

import logging
from typing import List, Dict, Any, Optional

from ..models import Opportunity, OpportunityType
from ..config import settings
from .web_scraping_service import WebScrapingManager
from .job_board_scrapers import (
    IndeedScraper,
    LinkedInScraper,
    WellfoundScraper,
    GreenhouseScraper
)
from .hackathon_scrapers import (
    EventbriteHackathonScraper,
    HackerEarthHackathonScraper,
    UnstopHackathonScraper,
    InternshalaInternshipScraper
)

logger = logging.getLogger(__name__)


class WebScrapingOpportunityFetcher:
    """Main fetcher class that uses web scraping to get opportunities."""
    
    def __init__(self):
        """Initialize the web scraping fetcher."""
        self.manager = WebScrapingManager()
        self._setup_scrapers()
    
    def _setup_scrapers(self):
        """Setup all available scrapers."""
        if not settings.web_scraping_enabled:
            logger.warning("Web scraping is disabled in configuration")
            return
        
        try:
            # Job board scrapers
            self.manager.register_scraper("indeed", IndeedScraper())
            self.manager.register_scraper("linkedin", LinkedInScraper())
            self.manager.register_scraper("wellfound", WellfoundScraper())
            self.manager.register_scraper("greenhouse", GreenhouseScraper())
            
            # Hackathon scrapers
            self.manager.register_scraper("eventbrite", EventbriteHackathonScraper())
            self.manager.register_scraper("hackerearth", HackerEarthHackathonScraper())
            self.manager.register_scraper("unstop", UnstopHackathonScraper())
            
            # Internship scrapers
            self.manager.register_scraper("internshala", InternshalaInternshipScraper())
            
            logger.info("Successfully registered all web scrapers")
            
        except Exception as e:
            logger.error(f"Error setting up scrapers: {e}")
    
    def fetch_all_opportunities(self, limit_per_source: int = 20) -> List[Opportunity]:
        """
        Fetch opportunities from all sources using web scraping.
        
        Args:
            limit_per_source: Maximum opportunities to fetch from each source
            
        Returns:
            Combined list of all opportunities
        """
        if not settings.web_scraping_enabled:
            logger.warning("Web scraping is disabled, returning empty list")
            return []
        
        try:
            return self.manager.fetch_all_opportunities(limit_per_source)
        except Exception as e:
            logger.error(f"Error fetching all opportunities: {e}")
            return []
    
    def fetch_opportunities_by_type(self, opportunity_type: OpportunityType, limit: int = 30) -> List[Opportunity]:
        """
        Fetch opportunities of a specific type using web scraping.
        
        Args:
            opportunity_type: Type of opportunities to fetch
            limit: Maximum number of opportunities to fetch
            
        Returns:
            List of opportunities of the specified type
        """
        if not settings.web_scraping_enabled:
            logger.warning("Web scraping is disabled, returning empty list")
            return []
        
        try:
            return self.manager.fetch_opportunities_by_type(opportunity_type, limit)
        except Exception as e:
            logger.error(f"Error fetching opportunities by type: {e}")
            return []
    
    def fetch_jobs(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch job opportunities using web scraping.
        
        Args:
            limit: Maximum number of jobs to fetch
            **kwargs: Additional parameters (keywords, location, etc.)
            
        Returns:
            List of job opportunities
        """
        if not settings.web_scraping_enabled:
            logger.warning("Web scraping is disabled, returning empty list")
            return []
        
        try:
            job_scrapers = ["indeed", "linkedin", "wellfound", "greenhouse"]
            opportunities = []
            limit_per_source = limit // len(job_scrapers)
            
            for scraper_name in job_scrapers:
                scraper = self.manager.get_scraper(scraper_name)
                if scraper:
                    try:
                        source_opportunities = scraper.fetch_opportunities(limit=limit_per_source, **kwargs)
                        opportunities.extend(source_opportunities)
                        logger.info(f"Fetched {len(source_opportunities)} jobs from {scraper_name}")
                    except Exception as e:
                        logger.error(f"Error fetching jobs from {scraper_name}: {e}")
                        continue
            
            logger.info(f"Total jobs fetched: {len(opportunities)}")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error fetching jobs: {e}")
            return []
    
    def fetch_hackathons(self, limit: int = 30, **kwargs) -> List[Opportunity]:
        """
        Fetch hackathon opportunities using web scraping.
        
        Args:
            limit: Maximum number of hackathons to fetch
            **kwargs: Additional parameters (keywords, location, etc.)
            
        Returns:
            List of hackathon opportunities
        """
        if not settings.web_scraping_enabled:
            logger.warning("Web scraping is disabled, returning empty list")
            return []
        
        try:
            hackathon_scrapers = ["eventbrite", "hackerearth", "unstop"]
            opportunities = []
            limit_per_source = limit // len(hackathon_scrapers)
            
            for scraper_name in hackathon_scrapers:
                scraper = self.manager.get_scraper(scraper_name)
                if scraper:
                    try:
                        source_opportunities = scraper.fetch_opportunities(limit=limit_per_source, **kwargs)
                        opportunities.extend(source_opportunities)
                        logger.info(f"Fetched {len(source_opportunities)} hackathons from {scraper_name}")
                    except Exception as e:
                        logger.error(f"Error fetching hackathons from {scraper_name}: {e}")
                        continue
            
            logger.info(f"Total hackathons fetched: {len(opportunities)}")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error fetching hackathons: {e}")
            return []
    
    def fetch_internships(self, limit: int = 30, **kwargs) -> List[Opportunity]:
        """
        Fetch internship opportunities using web scraping.
        
        Args:
            limit: Maximum number of internships to fetch
            **kwargs: Additional parameters (keywords, location, etc.)
            
        Returns:
            List of internship opportunities
        """
        if not settings.web_scraping_enabled:
            logger.warning("Web scraping is disabled, returning empty list")
            return []
        
        try:
            internship_scrapers = ["internshala"]
            opportunities = []
            limit_per_source = limit // len(internship_scrapers)
            
            for scraper_name in internship_scrapers:
                scraper = self.manager.get_scraper(scraper_name)
                if scraper:
                    try:
                        source_opportunities = scraper.fetch_opportunities(limit=limit_per_source, **kwargs)
                        opportunities.extend(source_opportunities)
                        logger.info(f"Fetched {len(source_opportunities)} internships from {scraper_name}")
                    except Exception as e:
                        logger.error(f"Error fetching internships from {scraper_name}: {e}")
                        continue
            
            logger.info(f"Total internships fetched: {len(opportunities)}")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error fetching internships: {e}")
            return []
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            self.manager.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Cleanup on deletion."""
        self.cleanup()


# Global instance for backward compatibility
web_scraping_fetcher = WebScrapingOpportunityFetcher()


def get_web_scraping_fetcher() -> WebScrapingOpportunityFetcher:
    """Get the global web scraping fetcher instance."""
    return web_scraping_fetcher



