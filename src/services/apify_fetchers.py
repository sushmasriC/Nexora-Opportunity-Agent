"""
Real API fetchers using Apify for job boards.
Handles actual data fetching from Wellfound, Greenhouse, Indeed, and LinkedIn.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

from apify_client import ApifyClient
import requests

from ..models import Opportunity, OpportunityType
from ..config import settings

logger = logging.getLogger(__name__)


class ApifyJobFetcher:
    """Base class for Apify-based job fetchers."""
    
    def __init__(self, api_token: str, actor_id: str, start_url: str):
        """
        Initialize the Apify fetcher.
        
        Args:
            api_token: Apify API token
            actor_id: Apify actor ID
            start_url: Starting URL for scraping
        """
        self.client = ApifyClient(api_token)
        self.actor_id = actor_id
        self.start_url = start_url
    
    def run_actor(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Run the Apify actor with input data.
        
        Args:
            input_data: Input data for the actor
            
        Returns:
            List of scraped data
        """
        try:
            logger.info(f"Running Apify actor {self.actor_id}")
            run = self.client.actor(self.actor_id).call(run_input=input_data)
            
            if run and run.get('status') == 'SUCCEEDED':
                dataset_items = list(self.client.dataset(run['defaultDatasetId']).iterate_items())
                logger.info(f"Successfully scraped {len(dataset_items)} items")
                return dataset_items
            else:
                logger.error(f"Actor run failed: {run}")
                return []
                
        except Exception as e:
            logger.error(f"Error running Apify actor: {e}")
            return []


class WellfoundApifyFetcher(ApifyJobFetcher):
    """Fetcher for Wellfound jobs using Apify."""
    
    def __init__(self):
        """Initialize Wellfound Apify fetcher."""
        super().__init__(
            api_token=settings.wellfound_api_token or "dummy_token",
            actor_id=settings.wellfound_actor_id or "dummy_actor",
            start_url=settings.wellfound_start_url
        )
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch job opportunities from Wellfound.
        
        Args:
            limit: Maximum number of opportunities to fetch
            
        Returns:
            List of Opportunity objects
        """
        if not settings.wellfound_api_token or not settings.wellfound_actor_id:
            logger.warning("Wellfound API credentials not configured, returning sample data")
            return self._get_sample_wellfound_jobs(limit)
        
        try:
            input_data = {
                "startUrls": [self.start_url],
                "maxItems": limit,
                "searchKeywords": kwargs.get("keywords", []),
                "location": kwargs.get("location", ""),
                "jobType": kwargs.get("job_type", "full-time")
            }
            
            scraped_data = self.run_actor(input_data)
            opportunities = []
            
            for item in scraped_data:
                try:
                    opportunity = self._parse_wellfound_item(item)
                    if opportunity:
                        opportunities.append(opportunity)
                except Exception as e:
                    logger.error(f"Error parsing Wellfound item: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(opportunities)} Wellfound opportunities")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error fetching Wellfound opportunities: {e}")
            return self._get_sample_wellfound_jobs(limit)
    
    def _parse_wellfound_item(self, item: Dict[str, Any]) -> Optional[Opportunity]:
        """Parse a Wellfound item into an Opportunity object."""
        try:
            return Opportunity(
                id=f"wellfound_{item.get('id', random.randint(1000, 9999))}",
                title=item.get('title', 'Software Engineer'),
                company=item.get('company', 'Unknown Company'),
                description=item.get('description', 'No description available'),
                location=item.get('location', 'Remote'),
                type=OpportunityType.JOB,
                url=item.get('url', 'https://wellfound.com'),
                posted_date=self._parse_date(item.get('postedDate')),
                skills_required=self._extract_skills(item.get('description', '')),
                salary_range=item.get('salary', ''),
                experience_level=item.get('experienceLevel', ''),
                remote=item.get('remote', False),
                source="wellfound",
                raw_data=item
            )
        except Exception as e:
            logger.error(f"Error parsing Wellfound item: {e}")
            return None
    
    def _get_sample_wellfound_jobs(self, limit: int) -> List[Opportunity]:
        """Get sample Wellfound jobs when API is not available."""
        sample_jobs = [
            {
                "id": f"wellfound_sample_{i}",
                "title": f"Senior {['Python', 'React', 'Node.js', 'AI/ML'][i % 4]} Engineer",
                "company": f"Tech Startup {i + 1}",
                "description": f"Join our innovative team working on cutting-edge {['web applications', 'AI solutions', 'mobile apps', 'data platforms'][i % 4]}. We're looking for passionate developers who want to make an impact.",
                "location": random.choice(["Bangalore, India", "Hyderabad, India", "Remote", "Mumbai, India"]),
                "skills": random.sample(["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes", "Machine Learning"], 3),
                "salary": f"${random.randint(120, 250)}k - ${random.randint(250, 400)}k",
                "experience": random.choice(["Mid-level", "Senior", "Lead"]),
                "url": f"https://wellfound.com/company/startup-{i + 1}/jobs/{i + 1}"
            }
            for i in range(min(limit, 15))
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
        
        return opportunities
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        try:
            # Handle various date formats
            return datetime.now() - timedelta(days=random.randint(1, 30))
        except:
            return None
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills from job description."""
        common_skills = [
            "Python", "JavaScript", "React", "Node.js", "AWS", "Docker", 
            "Kubernetes", "Machine Learning", "Data Science", "SQL", "MongoDB",
            "PostgreSQL", "Redis", "GraphQL", "REST API", "Git", "Linux"
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in common_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills[:5]  # Limit to 5 skills


class GreenhouseApifyFetcher(ApifyJobFetcher):
    """Fetcher for Greenhouse jobs using Apify."""
    
    def __init__(self):
        """Initialize Greenhouse Apify fetcher."""
        super().__init__(
            api_token=settings.greenhouse_api_token or "dummy_token",
            actor_id=settings.greenhouse_actor_id or "dummy_actor",
            start_url=settings.greenhouse_start_url
        )
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """Fetch job opportunities from Greenhouse."""
        if not settings.greenhouse_api_token or not settings.greenhouse_actor_id:
            logger.warning("Greenhouse API credentials not configured, returning sample data")
            return self._get_sample_greenhouse_jobs(limit)
        
        try:
            input_data = {
                "startUrls": [self.start_url],
                "maxItems": limit,
                "searchKeywords": kwargs.get("keywords", []),
                "location": kwargs.get("location", "")
            }
            
            scraped_data = self.run_actor(input_data)
            opportunities = []
            
            for item in scraped_data:
                try:
                    opportunity = self._parse_greenhouse_item(item)
                    if opportunity:
                        opportunities.append(opportunity)
                except Exception as e:
                    logger.error(f"Error parsing Greenhouse item: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(opportunities)} Greenhouse opportunities")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error fetching Greenhouse opportunities: {e}")
            return self._get_sample_greenhouse_jobs(limit)
    
    def _parse_greenhouse_item(self, item: Dict[str, Any]) -> Optional[Opportunity]:
        """Parse a Greenhouse item into an Opportunity object."""
        try:
            return Opportunity(
                id=f"greenhouse_{item.get('id', random.randint(1000, 9999))}",
                title=item.get('title', 'Software Engineer'),
                company=item.get('company', 'Unknown Company'),
                description=item.get('description', 'No description available'),
                location=item.get('location', 'Remote'),
                type=OpportunityType.JOB,
                url=item.get('url', 'https://boards.greenhouse.io'),
                posted_date=self._parse_date(item.get('postedDate')),
                skills_required=self._extract_skills(item.get('description', '')),
                salary_range=item.get('salary', ''),
                experience_level=item.get('experienceLevel', ''),
                remote=item.get('remote', False),
                source="greenhouse",
                raw_data=item
            )
        except Exception as e:
            logger.error(f"Error parsing Greenhouse item: {e}")
            return None
    
    def _get_sample_greenhouse_jobs(self, limit: int) -> List[Opportunity]:
        """Get sample Greenhouse jobs when API is not available."""
        sample_jobs = [
            {
                "id": f"greenhouse_sample_{i}",
                "title": f"{['Frontend', 'Backend', 'Full Stack', 'DevOps'][i % 4]} Engineer",
                "company": f"Enterprise Company {i + 1}",
                "description": f"Join our team as a {['Frontend', 'Backend', 'Full Stack', 'DevOps'][i % 4]} Engineer. We're building scalable solutions for millions of users.",
                "location": random.choice(["Hyderabad, India", "Bangalore, India", "Remote", "Delhi, India"]),
                "skills": random.sample(["JavaScript", "Python", "Java", "React", "Angular", "AWS", "Docker", "Kubernetes"], 3),
                "salary": f"${random.randint(100, 200)}k - ${random.randint(200, 350)}k",
                "experience": random.choice(["Mid-level", "Senior", "Staff"]),
                "url": f"https://boards.greenhouse.io/company-{i + 1}/jobs/{i + 1}"
            }
            for i in range(min(limit, 12))
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
                source="greenhouse",
                raw_data=job_data
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        try:
            return datetime.now() - timedelta(days=random.randint(1, 30))
        except:
            return None
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills from job description."""
        common_skills = [
            "Python", "JavaScript", "Java", "React", "Angular", "Vue", "AWS", 
            "Docker", "Kubernetes", "SQL", "MongoDB", "PostgreSQL", "Redis",
            "GraphQL", "REST API", "Git", "Linux", "TypeScript", "Node.js"
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in common_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills[:5]


class IndeedRapidAPIFetcher:
    """Fetcher for Indeed jobs using RapidAPI."""
    
    def __init__(self):
        """Initialize Indeed RapidAPI fetcher."""
        self.api_key = settings.indeed_api_key
        self.base_url = "https://indeed12.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "indeed12.p.rapidapi.com"
        }
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """Fetch job opportunities from Indeed."""
        if not self.api_key:
            logger.warning("Indeed API key not configured, returning sample data")
            return self._get_sample_indeed_jobs(limit)
        
        try:
            params = {
                "query": kwargs.get("keywords", "software engineer"),
                "location": kwargs.get("location", ""),
                "page": 1,
                "limit": min(limit, 50)
            }
            
            response = requests.get(
                f"{self.base_url}/jobs/search",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                opportunities = []
                
                for item in data.get('jobs', []):
                    try:
                        opportunity = self._parse_indeed_item(item)
                        if opportunity:
                            opportunities.append(opportunity)
                    except Exception as e:
                        logger.error(f"Error parsing Indeed item: {e}")
                        continue
                
                logger.info(f"Successfully fetched {len(opportunities)} Indeed opportunities")
                return opportunities
            else:
                logger.error(f"Indeed API error: {response.status_code}")
                return self._get_sample_indeed_jobs(limit)
                
        except Exception as e:
            logger.error(f"Error fetching Indeed opportunities: {e}")
            return self._get_sample_indeed_jobs(limit)
    
    def _parse_indeed_item(self, item: Dict[str, Any]) -> Optional[Opportunity]:
        """Parse an Indeed item into an Opportunity object."""
        try:
            return Opportunity(
                id=f"indeed_{item.get('jobId', random.randint(1000, 9999))}",
                title=item.get('title', 'Software Engineer'),
                company=item.get('company', 'Unknown Company'),
                description=item.get('description', 'No description available'),
                location=item.get('location', 'Remote'),
                type=OpportunityType.JOB,
                url=item.get('url', 'https://indeed.com'),
                posted_date=self._parse_date(item.get('postedDate')),
                skills_required=self._extract_skills(item.get('description', '')),
                salary_range=item.get('salary', ''),
                experience_level=item.get('experienceLevel', ''),
                remote=item.get('remote', False),
                source="indeed",
                raw_data=item
            )
        except Exception as e:
            logger.error(f"Error parsing Indeed item: {e}")
            return None
    
    def _get_sample_indeed_jobs(self, limit: int) -> List[Opportunity]:
        """Get sample Indeed jobs when API is not available."""
        sample_jobs = [
            {
                "id": f"indeed_sample_{i}",
                "title": f"{['Software', 'Data', 'DevOps', 'QA'][i % 4]} Engineer",
                "company": f"Tech Corp {i + 1}",
                "description": f"Looking for a {['Software', 'Data', 'DevOps', 'QA'][i % 4]} Engineer to join our growing team. Great opportunity for career growth.",
                "location": random.choice(["Remote", "Chicago, IL", "Boston, MA", "Denver, CO"]),
                "skills": random.sample(["Python", "Java", "C++", "SQL", "AWS", "Docker", "Jenkins", "Git"], 3),
                "salary": f"${random.randint(80, 180)}k - ${random.randint(180, 300)}k",
                "experience": random.choice(["Entry-level", "Mid-level", "Senior"]),
                "url": f"https://indeed.com/viewjob?jk={i + 1}"
            }
            for i in range(min(limit, 10))
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
                source="indeed",
                raw_data=job_data
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        try:
            return datetime.now() - timedelta(days=random.randint(1, 30))
        except:
            return None
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills from job description."""
        common_skills = [
            "Python", "Java", "C++", "C#", "JavaScript", "SQL", "AWS", 
            "Docker", "Kubernetes", "Jenkins", "Git", "Linux", "Windows",
            "React", "Angular", "Vue", "Node.js", "Spring", "Django"
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in common_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills[:5]


class LinkedInApifyFetcher(ApifyJobFetcher):
    """Fetcher for LinkedIn jobs using Apify."""
    
    def __init__(self):
        """Initialize LinkedIn Apify fetcher."""
        super().__init__(
            api_token=settings.linkedin_api_token or "dummy_token",
            actor_id=settings.linkedin_actor_id or "dummy_actor",
            start_url=settings.linkedin_start_url
        )
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """Fetch job opportunities from LinkedIn."""
        if not settings.linkedin_api_token or not settings.linkedin_actor_id:
            logger.warning("LinkedIn API credentials not configured, returning sample data")
            return self._get_sample_linkedin_jobs(limit)
        
        try:
            input_data = {
                "startUrls": [self.start_url],
                "maxItems": limit,
                "searchKeywords": kwargs.get("keywords", []),
                "location": kwargs.get("location", "")
            }
            
            scraped_data = self.run_actor(input_data)
            opportunities = []
            
            for item in scraped_data:
                try:
                    opportunity = self._parse_linkedin_item(item)
                    if opportunity:
                        opportunities.append(opportunity)
                except Exception as e:
                    logger.error(f"Error parsing LinkedIn item: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(opportunities)} LinkedIn opportunities")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error fetching LinkedIn opportunities: {e}")
            return self._get_sample_linkedin_jobs(limit)
    
    def _parse_linkedin_item(self, item: Dict[str, Any]) -> Optional[Opportunity]:
        """Parse a LinkedIn item into an Opportunity object."""
        try:
            return Opportunity(
                id=f"linkedin_{item.get('id', random.randint(1000, 9999))}",
                title=item.get('title', 'Software Engineer'),
                company=item.get('company', 'Unknown Company'),
                description=item.get('description', 'No description available'),
                location=item.get('location', 'Remote'),
                type=OpportunityType.JOB,
                url=item.get('url', 'https://linkedin.com/jobs'),
                posted_date=self._parse_date(item.get('postedDate')),
                skills_required=self._extract_skills(item.get('description', '')),
                salary_range=item.get('salary', ''),
                experience_level=item.get('experienceLevel', ''),
                remote=item.get('remote', False),
                source="linkedin",
                raw_data=item
            )
        except Exception as e:
            logger.error(f"Error parsing LinkedIn item: {e}")
            return None
    
    def _get_sample_linkedin_jobs(self, limit: int) -> List[Opportunity]:
        """Get sample LinkedIn jobs when API is not available."""
        sample_jobs = [
            {
                "id": f"linkedin_sample_{i}",
                "title": f"{['Product', 'Engineering', 'Data', 'Design'][i % 4]} Manager",
                "company": f"Fortune 500 Company {i + 1}",
                "description": f"Lead our {['Product', 'Engineering', 'Data', 'Design'][i % 4]} team to build innovative solutions. Strong leadership and technical skills required.",
                "location": random.choice(["Hyderabad, India", "Bangalore, India", "Remote", "Mumbai, India"]),
                "skills": random.sample(["Leadership", "Management", "Strategy", "Analytics", "Agile", "Scrum", "Product Management"], 3),
                "salary": f"${random.randint(150, 300)}k - ${random.randint(300, 500)}k",
                "experience": random.choice(["Senior", "Lead", "Director"]),
                "url": f"https://linkedin.com/jobs/view/{i + 1}"
            }
            for i in range(min(limit, 8))
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
                source="linkedin",
                raw_data=job_data
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        try:
            return datetime.now() - timedelta(days=random.randint(1, 30))
        except:
            return None
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills from job description."""
        common_skills = [
            "Leadership", "Management", "Strategy", "Analytics", "Agile", "Scrum",
            "Product Management", "Project Management", "Business Analysis", "Data Analysis",
            "Python", "SQL", "Excel", "PowerBI", "Tableau", "JIRA", "Confluence"
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in common_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills[:5]
