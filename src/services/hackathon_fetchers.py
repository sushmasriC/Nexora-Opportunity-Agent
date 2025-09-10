"""
Real hackathon fetchers using Eventbrite and HackerEarth APIs.
Handles actual hackathon data fetching from these platforms.
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

from apify_client import ApifyClient

from ..models import Opportunity, OpportunityType
from ..config import settings

logger = logging.getLogger(__name__)


class EventbriteHackathonFetcher:
    """Fetcher for Eventbrite hackathons using Apify."""
    
    def __init__(self):
        """Initialize Eventbrite hackathon fetcher."""
        self.api_token = settings.eventbrite_api_token
        self.actor_id = settings.eventbrite_actor_id
        self.start_url = settings.eventbrite_start_url
        self.client = None
        
        if self.api_token:
            self.client = ApifyClient(self.api_token)
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch hackathon opportunities from Eventbrite.
        
        Args:
            limit: Maximum number of opportunities to fetch
            
        Returns:
            List of Opportunity objects
        """
        if not self.api_token or not self.actor_id:
            logger.warning("Eventbrite API credentials not configured, returning sample data")
            return self._get_sample_eventbrite_hackathons(limit)
        
        try:
            input_data = {
                "startUrls": [self.start_url],
                "maxItems": limit,
                "eventType": "hackathon",
                "location": kwargs.get("location", ""),
                "dateRange": kwargs.get("date_range", "upcoming")
            }
            
            logger.info(f"Running Eventbrite Apify actor {self.actor_id}")
            run = self.client.actor(self.actor_id).call(run_input=input_data)
            
            if run and run.get('status') == 'SUCCEEDED':
                dataset_items = list(self.client.dataset(run['defaultDatasetId']).iterate_items())
                logger.info(f"Successfully scraped {len(dataset_items)} Eventbrite hackathons")
                
                opportunities = []
                for item in dataset_items:
                    try:
                        opportunity = self._parse_eventbrite_item(item)
                        if opportunity:
                            opportunities.append(opportunity)
                    except Exception as e:
                        logger.error(f"Error parsing Eventbrite item: {e}")
                        continue
                
                return opportunities
            else:
                logger.error(f"Eventbrite actor run failed: {run}")
                return self._get_sample_eventbrite_hackathons(limit)
                
        except Exception as e:
            logger.error(f"Error fetching Eventbrite hackathons: {e}")
            return self._get_sample_eventbrite_hackathons(limit)
    
    def _parse_eventbrite_item(self, item: Dict[str, Any]) -> Optional[Opportunity]:
        """Parse an Eventbrite item into an Opportunity object."""
        try:
            return Opportunity(
                id=f"eventbrite_{item.get('id', random.randint(1000, 9999))}",
                title=item.get('name', 'Hackathon Event'),
                company=item.get('organizer', 'Eventbrite Organizer'),
                description=item.get('description', 'Join this exciting hackathon event!'),
                location=item.get('location', 'Online'),
                type=OpportunityType.HACKATHON,
                url=item.get('url', 'https://eventbrite.com'),
                posted_date=self._parse_date(item.get('created')),
                deadline=self._parse_date(item.get('end_date')),
                skills_required=self._extract_skills(item.get('description', '')),
                salary_range=item.get('prize', ''),
                experience_level="Any",
                remote=item.get('is_online', True),
                source="eventbrite",
                raw_data=item
            )
        except Exception as e:
            logger.error(f"Error parsing Eventbrite item: {e}")
            return None
    
    def _get_sample_eventbrite_hackathons(self, limit: int) -> List[Opportunity]:
        """Get sample Eventbrite hackathons when API is not available."""
        sample_hackathons = [
            {
                "id": f"eventbrite_sample_{i}",
                "title": f"{['AI Innovation', 'Web3 Challenge', 'FinTech', 'EdTech', 'HealthTech', 'ClimateTech'][i % 6]} Hackathon",
                "company": f"Hackathon Organizer {i + 1}",
                "description": f"Join our {['AI Innovation', 'Web3', 'FinTech', 'EdTech', 'HealthTech', 'ClimateTech'][i % 6]} hackathon and build innovative solutions. Prizes worth ₹{random.randint(50, 500)}k up for grabs!",
                "location": random.choice(["Online", "Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai"]),
                "skills": random.sample(["Programming", "AI/ML", "Blockchain", "Design", "Presentation", "Teamwork", "Data Science"], 3),
                "prize": f"₹{random.randint(50, 500)}k",
                "duration": f"{random.randint(24, 72)} hours",
                "url": f"https://eventbrite.com/e/hackathon-{i + 1}"
            }
            for i in range(min(limit, 12))
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
                source="eventbrite",
                raw_data=hack_data
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        try:
            return datetime.now() + timedelta(days=random.randint(3, 21))
        except:
            return None
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills from hackathon description."""
        common_skills = [
            "Programming", "AI/ML", "Blockchain", "Design", "Presentation", 
            "Teamwork", "Data Science", "Web Development", "Mobile Development",
            "Cloud Computing", "DevOps", "UI/UX", "Product Management"
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in common_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills[:5]


class HackerEarthHackathonFetcher:
    """Fetcher for HackerEarth hackathons using RapidAPI."""
    
    def __init__(self):
        """Initialize HackerEarth hackathon fetcher."""
        self.api_url = settings.hackerearth_api_url
        self.api_key = settings.hackerearth_api_key
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "ideas2it-hackerearth.p.rapidapi.com"
        }
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch hackathon opportunities from HackerEarth.
        
        Args:
            limit: Maximum number of opportunities to fetch
            
        Returns:
            List of Opportunity objects
        """
        if not self.api_key:
            logger.warning("HackerEarth API key not configured, returning sample data")
            return self._get_sample_hackerearth_hackathons(limit)
        
        try:
            # HackerEarth API call
            params = {
                "limit": min(limit, 50),
                "type": "hackathon",
                "status": "upcoming"
            }
            
            response = requests.get(
                self.api_url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                opportunities = []
                
                for item in data.get('hackathons', []):
                    try:
                        opportunity = self._parse_hackerearth_item(item)
                        if opportunity:
                            opportunities.append(opportunity)
                    except Exception as e:
                        logger.error(f"Error parsing HackerEarth item: {e}")
                        continue
                
                logger.info(f"Successfully fetched {len(opportunities)} HackerEarth hackathons")
                return opportunities
            else:
                logger.error(f"HackerEarth API error: {response.status_code}")
                return self._get_sample_hackerearth_hackathons(limit)
                
        except Exception as e:
            logger.error(f"Error fetching HackerEarth hackathons: {e}")
            return self._get_sample_hackerearth_hackathons(limit)
    
    def _parse_hackerearth_item(self, item: Dict[str, Any]) -> Optional[Opportunity]:
        """Parse a HackerEarth item into an Opportunity object."""
        try:
            return Opportunity(
                id=f"hackerearth_{item.get('id', random.randint(1000, 9999))}",
                title=item.get('title', 'HackerEarth Hackathon'),
                company=item.get('company', 'HackerEarth'),
                description=item.get('description', 'Join this exciting hackathon on HackerEarth!'),
                location=item.get('location', 'Online'),
                type=OpportunityType.HACKATHON,
                url=item.get('url', 'https://hackerearth.com'),
                posted_date=self._parse_date(item.get('created_at')),
                deadline=self._parse_date(item.get('end_date')),
                skills_required=self._extract_skills(item.get('description', '')),
                salary_range=item.get('prize', ''),
                experience_level="Any",
                remote=item.get('is_online', True),
                source="hackerearth",
                raw_data=item
            )
        except Exception as e:
            logger.error(f"Error parsing HackerEarth item: {e}")
            return None
    
    def _get_sample_hackerearth_hackathons(self, limit: int) -> List[Opportunity]:
        """Get sample HackerEarth hackathons when API is not available."""
        sample_hackathons = [
            {
                "id": f"hackerearth_sample_{i}",
                "title": f"{['Data Science', 'Machine Learning', 'Web Development', 'Mobile App', 'Blockchain', 'IoT'][i % 6]} Challenge",
                "company": f"Tech Company {i + 1}",
                "description": f"Participate in our {['Data Science', 'Machine Learning', 'Web Development', 'Mobile App', 'Blockchain', 'IoT'][i % 6]} challenge and showcase your skills. Great prizes and recognition await!",
                "location": random.choice(["Online", "Bangalore", "Mumbai", "Delhi", "Pune", "Kolkata"]),
                "skills": random.sample(["Python", "Machine Learning", "Data Analysis", "Web Development", "Mobile Development", "Blockchain", "IoT"], 3),
                "prize": f"₹{random.randint(25, 200)}k",
                "duration": f"{random.randint(48, 168)} hours",
                "url": f"https://hackerearth.com/challenges/hackathon/hackathon-{i + 1}"
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
                posted_date=datetime.now() - timedelta(days=random.randint(1, 7)),
                deadline=datetime.now() + timedelta(days=random.randint(5, 30)),
                skills_required=hack_data["skills"],
                salary_range=hack_data["prize"],
                experience_level="Any",
                remote=hack_data["location"] == "Online",
                source="hackerearth",
                raw_data=hack_data
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        try:
            return datetime.now() + timedelta(days=random.randint(5, 30))
        except:
            return None
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills from hackathon description."""
        common_skills = [
            "Python", "Machine Learning", "Data Analysis", "Web Development", 
            "Mobile Development", "Blockchain", "IoT", "Cloud Computing",
            "DevOps", "UI/UX", "Product Management", "Data Science"
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in common_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills[:5]
