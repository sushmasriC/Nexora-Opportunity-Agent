"""
Web scraping service for fetching opportunities from various platforms.
Provides base classes and utilities for scraping job boards and hackathon platforms.
"""

import asyncio
import logging
import random
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests_html import AsyncHTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..models import Opportunity, OpportunityType
from ..config import settings

logger = logging.getLogger(__name__)


class WebScrapingError(Exception):
    """Custom exception for web scraping errors."""
    pass


class BaseWebScraper(ABC):
    """Base class for web scrapers."""
    
    def __init__(self, base_url: str, delay_range: tuple = (1, 3)):
        """
        Initialize the web scraper.
        
        Args:
            base_url: Base URL for the platform
            delay_range: Tuple of (min, max) delay between requests in seconds
        """
        self.base_url = base_url
        self.delay_range = delay_range
        self.session = requests.Session()
        self.ua = UserAgent()
        self._setup_session()
    
    def _setup_session(self):
        """Setup the requests session with headers and configuration."""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def _get_random_delay(self) -> float:
        """Get a random delay between requests."""
        return random.uniform(*self.delay_range)
    
    def _make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Make a request with error handling and rate limiting.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object or None if failed
        """
        try:
            # Add random delay to avoid being blocked
            time.sleep(self._get_random_delay())
            
            # Update user agent for each request
            self.session.headers['User-Agent'] = self.ua.random
            
            response = self.session.get(url, timeout=30, **kwargs)
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse various date formats to datetime object.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            Datetime object or None if parsing fails
        """
        if not date_str:
            return None
        
        # Common date formats
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%B %d, %Y',
            '%b %d, %Y',
            '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        # If no format matches, try to extract relative dates
        date_str_lower = date_str.lower().strip()
        now = datetime.now()
        
        if 'today' in date_str_lower:
            return now
        elif 'yesterday' in date_str_lower:
            return now - timedelta(days=1)
        elif 'day' in date_str_lower and any(char.isdigit() for char in date_str):
            # Extract number of days
            import re
            days_match = re.search(r'(\d+)', date_str)
            if days_match:
                days = int(days_match.group(1))
                return now - timedelta(days=days)
        
        # Default to random recent date if parsing fails
        return now - timedelta(days=random.randint(1, 30))
    
    def _extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from text using common skill keywords.
        
        Args:
            text: Text to extract skills from
            
        Returns:
            List of found skills
        """
        common_skills = [
            # Programming Languages
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'Swift', 'Kotlin',
            'PHP', 'Ruby', 'TypeScript', 'Scala', 'R', 'MATLAB', 'Perl', 'Haskell',
            
            # Web Technologies
            'React', 'Angular', 'Vue.js', 'Node.js', 'Express', 'Django', 'Flask',
            'Spring', 'Laravel', 'Rails', 'ASP.NET', 'jQuery', 'Bootstrap', 'Tailwind',
            
            # Databases
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Cassandra',
            'DynamoDB', 'SQLite', 'Oracle', 'SQL Server',
            
            # Cloud & DevOps
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI',
            'GitHub Actions', 'Terraform', 'Ansible', 'Chef', 'Puppet',
            
            # Data & AI
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn',
            'Pandas', 'NumPy', 'Data Science', 'Data Analysis', 'Statistics',
            
            # Mobile
            'iOS', 'Android', 'React Native', 'Flutter', 'Xamarin', 'Ionic',
            
            # Other
            'Git', 'Linux', 'Windows', 'Agile', 'Scrum', 'DevOps', 'Microservices',
            'REST API', 'GraphQL', 'WebSocket', 'OAuth', 'JWT'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills[:10]  # Limit to 10 skills
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        
        # Remove common unwanted characters
        unwanted_chars = ['\n', '\r', '\t', '\xa0']
        for char in unwanted_chars:
            text = text.replace(char, ' ')
        
        return text.strip()
    
    @abstractmethod
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch opportunities from the platform.
        
        Args:
            limit: Maximum number of opportunities to fetch
            **kwargs: Additional parameters for fetching
            
        Returns:
            List of Opportunity objects
        """
        pass


class SeleniumScraper(BaseWebScraper):
    """Base class for scrapers that require JavaScript rendering."""
    
    def __init__(self, base_url: str, delay_range: tuple = (2, 5)):
        """
        Initialize the Selenium scraper.
        
        Args:
            base_url: Base URL for the platform
            delay_range: Tuple of (min, max) delay between requests in seconds
        """
        super().__init__(base_url, delay_range)
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """Setup Chrome driver with options."""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(f'--user-agent={self.ua.random}')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            self.driver = None
    
    def _wait_for_element(self, by: By, value: str, timeout: int = 10) -> bool:
        """
        Wait for an element to be present on the page.
        
        Args:
            by: Selenium By selector
            value: Selector value
            timeout: Maximum time to wait
            
        Returns:
            True if element found, False otherwise
        """
        if not self.driver:
            return False
        
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False
    
    def _scroll_to_bottom(self, pause_time: float = 1.0):
        """
        Scroll to the bottom of the page to load more content.
        
        Args:
            pause_time: Time to pause between scrolls
        """
        if not self.driver:
            return
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait to load page
            time.sleep(pause_time)
            
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
    def close(self):
        """Close the driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()


class AsyncScraper(BaseWebScraper):
    """Base class for async scrapers using requests-html."""
    
    def __init__(self, base_url: str, delay_range: tuple = (1, 3)):
        """
        Initialize the async scraper.
        
        Args:
            base_url: Base URL for the platform
            delay_range: Tuple of (min, max) delay between requests in seconds
        """
        super().__init__(base_url, delay_range)
        self.session = AsyncHTMLSession()
    
    async def _make_async_request(self, url: str, **kwargs) -> Optional[Any]:
        """
        Make an async request with error handling.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object or None if failed
        """
        try:
            # Add random delay
            await asyncio.sleep(self._get_random_delay())
            
            response = await self.session.get(url, **kwargs)
            response.raise_for_status()
            
            return response
            
        except Exception as e:
            logger.error(f"Async request failed for {url}: {e}")
            return None
    
    async def close(self):
        """Close the async session."""
        if hasattr(self.session, 'close'):
            await self.session.close()


class WebScrapingManager:
    """Manager class for coordinating web scraping operations."""
    
    def __init__(self):
        """Initialize the scraping manager."""
        self.scrapers = {}
        self.active_scrapers = []
    
    def register_scraper(self, name: str, scraper: BaseWebScraper):
        """
        Register a scraper with the manager.
        
        Args:
            name: Name to register the scraper under
            scraper: Scraper instance
        """
        self.scrapers[name] = scraper
        logger.info(f"Registered scraper: {name}")
    
    def get_scraper(self, name: str) -> Optional[BaseWebScraper]:
        """
        Get a registered scraper by name.
        
        Args:
            name: Name of the scraper
            
        Returns:
            Scraper instance or None if not found
        """
        return self.scrapers.get(name)
    
    def fetch_all_opportunities(self, limit_per_source: int = 20) -> List[Opportunity]:
        """
        Fetch opportunities from all registered scrapers.
        
        Args:
            limit_per_source: Maximum opportunities to fetch from each source
            
        Returns:
            Combined list of all opportunities
        """
        all_opportunities = []
        
        for name, scraper in self.scrapers.items():
            try:
                logger.info(f"Fetching opportunities from {name}")
                opportunities = scraper.fetch_opportunities(limit=limit_per_source)
                all_opportunities.extend(opportunities)
                logger.info(f"Successfully fetched {len(opportunities)} opportunities from {name}")
            except Exception as e:
                logger.error(f"Error fetching opportunities from {name}: {e}")
                continue
        
        logger.info(f"Total opportunities fetched: {len(all_opportunities)}")
        return all_opportunities
    
    def fetch_opportunities_by_type(self, opportunity_type: OpportunityType, limit: int = 30) -> List[Opportunity]:
        """
        Fetch opportunities of a specific type.
        
        Args:
            opportunity_type: Type of opportunities to fetch
            limit: Maximum number of opportunities to fetch
            
        Returns:
            List of opportunities of the specified type
        """
        opportunities = []
        
        # Filter scrapers by type
        relevant_scrapers = []
        for name, scraper in self.scrapers.items():
            if hasattr(scraper, 'opportunity_type') and scraper.opportunity_type == opportunity_type:
                relevant_scrapers.append((name, scraper))
        
        limit_per_source = limit // max(len(relevant_scrapers), 1)
        
        for name, scraper in relevant_scrapers:
            try:
                source_opportunities = scraper.fetch_opportunities(limit=limit_per_source)
                opportunities.extend(source_opportunities)
            except Exception as e:
                logger.error(f"Error fetching from {name}: {e}")
                continue
        
        return opportunities
    
    def cleanup(self):
        """Cleanup all active scrapers."""
        for scraper in self.active_scrapers:
            try:
                if hasattr(scraper, 'close'):
                    if asyncio.iscoroutinefunction(scraper.close):
                        asyncio.run(scraper.close())
                    else:
                        scraper.close()
            except Exception as e:
                logger.error(f"Error cleaning up scraper: {e}")
        
        self.active_scrapers.clear()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.cleanup()



