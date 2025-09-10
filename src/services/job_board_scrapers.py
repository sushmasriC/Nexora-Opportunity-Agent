"""
Job board scrapers for fetching job opportunities from various platforms.
Implements scrapers for Indeed, LinkedIn, Wellfound, and Greenhouse.
"""

import logging
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlencode

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .web_scraping_service import BaseWebScraper, SeleniumScraper, WebScrapingError
from ..models import Opportunity, OpportunityType

logger = logging.getLogger(__name__)


class IndeedScraper(BaseWebScraper):
    """Scraper for Indeed job board."""
    
    def __init__(self):
        super().__init__("https://indeed.com", delay_range=(2, 4))
        self.opportunity_type = OpportunityType.JOB
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch job opportunities from Indeed.
        
        Args:
            limit: Maximum number of opportunities to fetch
            **kwargs: Additional parameters (keywords, location, etc.)
            
        Returns:
            List of Opportunity objects
        """
        try:
            keywords = kwargs.get('keywords', ['software engineer'])
            location = kwargs.get('location', '')
            
            # Build search URL
            search_params = {
                'q': ' '.join(keywords) if isinstance(keywords, list) else keywords,
                'l': location,
                'sort': 'date',
                'fromage': '7'  # Last 7 days
            }
            
            search_url = f"{self.base_url}/jobs?{urlencode(search_params)}"
            logger.info(f"Scraping Indeed jobs from: {search_url}")
            
            opportunities = []
            page = 0
            
            while len(opportunities) < limit and page < 10:  # Limit to 10 pages
                page_url = f"{search_url}&start={page * 10}"
                response = self._make_request(page_url)
                
                if not response:
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', {'data-jk': True})
                
                if not job_cards:
                    logger.info("No more job cards found, stopping pagination")
                    break
                
                for card in job_cards:
                    if len(opportunities) >= limit:
                        break
                    
                    try:
                        opportunity = self._parse_job_card(card)
                        if opportunity:
                            opportunities.append(opportunity)
                    except Exception as e:
                        logger.error(f"Error parsing job card: {e}")
                        continue
                
                page += 1
                time.sleep(self._get_random_delay())
            
            logger.info(f"Successfully scraped {len(opportunities)} jobs from Indeed")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}")
            return []
    
    def _parse_job_card(self, card) -> Optional[Opportunity]:
        """Parse a job card element into an Opportunity object."""
        try:
            # Extract job ID
            job_id = card.get('data-jk', '')
            if not job_id:
                return None
            
            # Extract title and company
            title_elem = card.find('h2', class_='jobTitle')
            title = self._clean_text(title_elem.get_text()) if title_elem else "Software Engineer"
            
            company_elem = card.find('span', class_='companyName')
            company = self._clean_text(company_elem.get_text()) if company_elem else "Unknown Company"
            
            # Extract location
            location_elem = card.find('div', class_='companyLocation')
            location = self._clean_text(location_elem.get_text()) if location_elem else "Remote"
            
            # Extract salary if available
            salary_elem = card.find('div', class_='salary-snippet')
            salary = self._clean_text(salary_elem.get_text()) if salary_elem else ""
            
            # Extract description snippet
            desc_elem = card.find('div', class_='job-snippet')
            description = self._clean_text(desc_elem.get_text()) if desc_elem else ""
            
            # Extract posted date
            date_elem = card.find('span', class_='date')
            posted_date = None
            if date_elem:
                date_text = self._clean_text(date_elem.get_text())
                posted_date = self._parse_date(date_text)
            
            # Build job URL
            job_url = f"{self.base_url}/viewjob?jk={job_id}"
            
            # Extract skills from description
            skills = self._extract_skills(description)
            
            return Opportunity(
                id=f"indeed_{job_id}",
                title=title,
                company=company,
                description=description,
                location=location,
                type=OpportunityType.JOB,
                url=job_url,
                posted_date=posted_date,
                skills_required=skills,
                salary_range=salary,
                experience_level=self._extract_experience_level(description),
                remote="remote" in location.lower(),
                source="indeed",
                raw_data={
                    'job_id': job_id,
                    'title': title,
                    'company': company,
                    'location': location,
                    'salary': salary,
                    'description': description
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing Indeed job card: {e}")
            return None
    
    def _extract_experience_level(self, text: str) -> str:
        """Extract experience level from job description."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['senior', 'lead', 'principal', 'staff']):
            return "Senior"
        elif any(word in text_lower for word in ['junior', 'entry', 'graduate', 'intern']):
            return "Entry-level"
        elif any(word in text_lower for word in ['mid', 'intermediate', 'experienced']):
            return "Mid-level"
        else:
            return "Not specified"


class LinkedInScraper(SeleniumScraper):
    """Scraper for LinkedIn job board using Selenium."""
    
    def __init__(self):
        super().__init__("https://linkedin.com/jobs", delay_range=(3, 6))
        self.opportunity_type = OpportunityType.JOB
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch job opportunities from LinkedIn.
        
        Args:
            limit: Maximum number of opportunities to fetch
            **kwargs: Additional parameters (keywords, location, etc.)
            
        Returns:
            List of Opportunity objects
        """
        if not self.driver:
            logger.error("Selenium driver not available for LinkedIn scraping")
            return []
        
        try:
            keywords = kwargs.get('keywords', ['software engineer'])
            location = kwargs.get('location', '')
            
            # Build search URL
            search_params = {
                'keywords': ' '.join(keywords) if isinstance(keywords, list) else keywords,
                'location': location,
                'sortBy': 'DD',  # Sort by date
                'f_TPR': 'r604800'  # Last 7 days
            }
            
            search_url = f"{self.base_url}/search?{urlencode(search_params)}"
            logger.info(f"Scraping LinkedIn jobs from: {search_url}")
            
            self.driver.get(search_url)
            
            # Wait for jobs to load
            if not self._wait_for_element(By.CLASS_NAME, "jobs-search-results-list", timeout=15):
                logger.error("Failed to load LinkedIn jobs page")
                return []
            
            opportunities = []
            processed_jobs = set()
            
            # Scroll to load more jobs
            self._scroll_to_bottom(pause_time=2.0)
            
            # Find all job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "li.jobs-search-results__list-item")
            
            for card in job_cards:
                if len(opportunities) >= limit:
                    break
                
                try:
                    opportunity = self._parse_linkedin_job_card(card)
                    if opportunity and opportunity.id not in processed_jobs:
                        opportunities.append(opportunity)
                        processed_jobs.add(opportunity.id)
                except Exception as e:
                    logger.error(f"Error parsing LinkedIn job card: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(opportunities)} jobs from LinkedIn")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
            return []
        finally:
            self.close()
    
    def _parse_linkedin_job_card(self, card) -> Optional[Opportunity]:
        """Parse a LinkedIn job card element into an Opportunity object."""
        try:
            # Extract job ID from data-entity-urn
            job_id_elem = card.find_element(By.CSS_SELECTOR, "a[data-entity-urn]")
            job_id = job_id_elem.get_attribute("data-entity-urn").split(":")[-1]
            
            # Extract title
            title_elem = card.find_element(By.CSS_SELECTOR, "a[data-entity-urn] h3")
            title = self._clean_text(title_elem.text)
            
            # Extract company
            company_elem = card.find_element(By.CSS_SELECTOR, "h4 a")
            company = self._clean_text(company_elem.text)
            
            # Extract location
            location_elem = card.find_element(By.CSS_SELECTOR, "div.job-search-card__location")
            location = self._clean_text(location_elem.text)
            
            # Extract job URL
            job_url = job_id_elem.get_attribute("href")
            
            # Extract posted date
            date_elem = card.find_element(By.CSS_SELECTOR, "time")
            posted_date = None
            if date_elem:
                date_text = self._clean_text(date_elem.text)
                posted_date = self._parse_date(date_text)
            
            # Try to get description (might be in a different element)
            description = ""
            try:
                desc_elem = card.find_element(By.CSS_SELECTOR, "div.job-search-card__snippet")
                description = self._clean_text(desc_elem.text)
            except NoSuchElementException:
                pass
            
            # Extract skills from description
            skills = self._extract_skills(description)
            
            return Opportunity(
                id=f"linkedin_{job_id}",
                title=title,
                company=company,
                description=description,
                location=location,
                type=OpportunityType.JOB,
                url=job_url,
                posted_date=posted_date,
                skills_required=skills,
                salary_range="",  # LinkedIn doesn't show salary in job cards
                experience_level=self._extract_experience_level(description),
                remote="remote" in location.lower(),
                source="linkedin",
                raw_data={
                    'job_id': job_id,
                    'title': title,
                    'company': company,
                    'location': location,
                    'description': description
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing LinkedIn job card: {e}")
            return None


class WellfoundScraper(BaseWebScraper):
    """Scraper for Wellfound (AngelList) job board."""
    
    def __init__(self):
        super().__init__("https://wellfound.com", delay_range=(2, 4))
        self.opportunity_type = OpportunityType.JOB
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch job opportunities from Wellfound.
        
        Args:
            limit: Maximum number of opportunities to fetch
            **kwargs: Additional parameters (keywords, location, etc.)
            
        Returns:
            List of Opportunity objects
        """
        try:
            keywords = kwargs.get('keywords', ['software engineer'])
            location = kwargs.get('location', '')
            
            # Build search URL
            search_params = {
                'q': ' '.join(keywords) if isinstance(keywords, list) else keywords,
                'location': location,
                'sort': 'newest'
            }
            
            search_url = f"{self.base_url}/jobs?{urlencode(search_params)}"
            logger.info(f"Scraping Wellfound jobs from: {search_url}")
            
            opportunities = []
            page = 1
            
            while len(opportunities) < limit and page <= 5:  # Limit to 5 pages
                page_url = f"{search_url}&page={page}"
                response = self._make_request(page_url)
                
                if not response:
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job-card')
                
                if not job_cards:
                    logger.info("No more job cards found, stopping pagination")
                    break
                
                for card in job_cards:
                    if len(opportunities) >= limit:
                        break
                    
                    try:
                        opportunity = self._parse_wellfound_job_card(card)
                        if opportunity:
                            opportunities.append(opportunity)
                    except Exception as e:
                        logger.error(f"Error parsing Wellfound job card: {e}")
                        continue
                
                page += 1
                time.sleep(self._get_random_delay())
            
            logger.info(f"Successfully scraped {len(opportunities)} jobs from Wellfound")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping Wellfound: {e}")
            return []
    
    def _parse_wellfound_job_card(self, card) -> Optional[Opportunity]:
        """Parse a Wellfound job card element into an Opportunity object."""
        try:
            # Extract job ID from data attributes or URL
            job_link = card.find('a', href=True)
            if not job_link:
                return None
            
            job_url = urljoin(self.base_url, job_link['href'])
            job_id = job_url.split('/')[-1]
            
            # Extract title
            title_elem = card.find('h3', class_='job-title')
            title = self._clean_text(title_elem.get_text()) if title_elem else "Software Engineer"
            
            # Extract company
            company_elem = card.find('div', class_='company-name')
            company = self._clean_text(company_elem.get_text()) if company_elem else "Unknown Company"
            
            # Extract location
            location_elem = card.find('div', class_='job-location')
            location = self._clean_text(location_elem.get_text()) if location_elem else "Remote"
            
            # Extract description
            desc_elem = card.find('div', class_='job-description')
            description = self._clean_text(desc_elem.get_text()) if desc_elem else ""
            
            # Extract salary if available
            salary_elem = card.find('div', class_='salary')
            salary = self._clean_text(salary_elem.get_text()) if salary_elem else ""
            
            # Extract posted date
            date_elem = card.find('time')
            posted_date = None
            if date_elem:
                date_text = self._clean_text(date_elem.get_text())
                posted_date = self._parse_date(date_text)
            
            # Extract skills from description
            skills = self._extract_skills(description)
            
            return Opportunity(
                id=f"wellfound_{job_id}",
                title=title,
                company=company,
                description=description,
                location=location,
                type=OpportunityType.JOB,
                url=job_url,
                posted_date=posted_date,
                skills_required=skills,
                salary_range=salary,
                experience_level=self._extract_experience_level(description),
                remote="remote" in location.lower(),
                source="wellfound",
                raw_data={
                    'job_id': job_id,
                    'title': title,
                    'company': company,
                    'location': location,
                    'salary': salary,
                    'description': description
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing Wellfound job card: {e}")
            return None


class GreenhouseScraper(BaseWebScraper):
    """Scraper for Greenhouse job board."""
    
    def __init__(self):
        super().__init__("https://boards.greenhouse.io", delay_range=(2, 4))
        self.opportunity_type = OpportunityType.JOB
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch job opportunities from Greenhouse.
        
        Args:
            limit: Maximum number of opportunities to fetch
            **kwargs: Additional parameters (keywords, location, etc.)
            
        Returns:
            List of Opportunity objects
        """
        try:
            # Greenhouse doesn't have a unified search, so we'll scrape from multiple companies
            # For now, we'll use a list of known companies that use Greenhouse
            companies = [
                "stripe", "airbnb", "github", "shopify", "dropbox", "uber",
                "lyft", "pinterest", "slack", "zoom", "notion", "figma"
            ]
            
            opportunities = []
            
            for company in companies[:5]:  # Limit to 5 companies
                if len(opportunities) >= limit:
                    break
                
                company_url = f"{self.base_url}/{company}"
                logger.info(f"Scraping Greenhouse jobs from: {company_url}")
                
                response = self._make_request(company_url)
                if not response:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='opening')
                
                for card in job_cards:
                    if len(opportunities) >= limit:
                        break
                    
                    try:
                        opportunity = self._parse_greenhouse_job_card(card, company)
                        if opportunity:
                            opportunities.append(opportunity)
                    except Exception as e:
                        logger.error(f"Error parsing Greenhouse job card: {e}")
                        continue
                
                time.sleep(self._get_random_delay())
            
            logger.info(f"Successfully scraped {len(opportunities)} jobs from Greenhouse")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping Greenhouse: {e}")
            return []
    
    def _parse_greenhouse_job_card(self, card, company: str) -> Optional[Opportunity]:
        """Parse a Greenhouse job card element into an Opportunity object."""
        try:
            # Extract job link
            job_link = card.find('a', href=True)
            if not job_link:
                return None
            
            job_url = urljoin(self.base_url, job_link['href'])
            job_id = job_url.split('/')[-1]
            
            # Extract title
            title_elem = card.find('a')
            title = self._clean_text(title_elem.get_text()) if title_elem else "Software Engineer"
            
            # Extract location
            location_elem = card.find('span', class_='location')
            location = self._clean_text(location_elem.get_text()) if location_elem else "Remote"
            
            # Extract description (usually in a separate element)
            description = ""
            desc_elem = card.find('div', class_='description')
            if desc_elem:
                description = self._clean_text(desc_elem.get_text())
            
            # Extract skills from description
            skills = self._extract_skills(description)
            
            return Opportunity(
                id=f"greenhouse_{company}_{job_id}",
                title=title,
                company=company.title(),
                description=description,
                location=location,
                type=OpportunityType.JOB,
                url=job_url,
                posted_date=datetime.now() - timedelta(days=1),  # Default to recent
                skills_required=skills,
                salary_range="",  # Greenhouse doesn't show salary in job listings
                experience_level=self._extract_experience_level(description),
                remote="remote" in location.lower(),
                source="greenhouse",
                raw_data={
                    'job_id': job_id,
                    'title': title,
                    'company': company,
                    'location': location,
                    'description': description
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing Greenhouse job card: {e}")
            return None



