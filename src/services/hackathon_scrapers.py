"""
Hackathon platform scrapers for fetching hackathon opportunities.
Implements scrapers for Eventbrite, HackerEarth, and Unstop.
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


class EventbriteHackathonScraper(BaseWebScraper):
    """Scraper for Eventbrite hackathon events."""
    
    def __init__(self):
        super().__init__("https://www.eventbrite.com", delay_range=(2, 4))
        self.opportunity_type = OpportunityType.HACKATHON
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch hackathon opportunities from Eventbrite.
        
        Args:
            limit: Maximum number of opportunities to fetch
            **kwargs: Additional parameters (keywords, location, etc.)
            
        Returns:
            List of Opportunity objects
        """
        try:
            keywords = kwargs.get('keywords', ['hackathon'])
            location = kwargs.get('location', '')
            
            # Build search URL for hackathons
            search_params = {
                'q': ' '.join(keywords) if isinstance(keywords, list) else keywords,
                'location': location,
                'categories': '102',  # Technology category
                'subcategories': '2001',  # Hackathon subcategory
                'sort': 'date',
                'start_date': 'today',
                'end_date': '2024-12-31'
            }
            
            search_url = f"{self.base_url}/d/online/hackathon/?{urlencode(search_params)}"
            logger.info(f"Scraping Eventbrite hackathons from: {search_url}")
            
            opportunities = []
            page = 1
            
            while len(opportunities) < limit and page <= 5:  # Limit to 5 pages
                page_url = f"{search_url}&page={page}"
                response = self._make_request(page_url)
                
                if not response:
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                event_cards = soup.find_all('div', class_='search-event-card-wrapper')
                
                if not event_cards:
                    logger.info("No more event cards found, stopping pagination")
                    break
                
                for card in event_cards:
                    if len(opportunities) >= limit:
                        break
                    
                    try:
                        opportunity = self._parse_eventbrite_event_card(card)
                        if opportunity:
                            opportunities.append(opportunity)
                    except Exception as e:
                        logger.error(f"Error parsing Eventbrite event card: {e}")
                        continue
                
                page += 1
                time.sleep(self._get_random_delay())
            
            logger.info(f"Successfully scraped {len(opportunities)} hackathons from Eventbrite")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping Eventbrite: {e}")
            return []
    
    def _parse_eventbrite_event_card(self, card) -> Optional[Opportunity]:
        """Parse an Eventbrite event card element into an Opportunity object."""
        try:
            # Extract event link
            event_link = card.find('a', href=True)
            if not event_link:
                return None
            
            event_url = urljoin(self.base_url, event_link['href'])
            event_id = event_url.split('/')[-1].split('-')[0]
            
            # Extract title
            title_elem = card.find('h3', class_='event-card__title')
            title = self._clean_text(title_elem.get_text()) if title_elem else "Hackathon Event"
            
            # Extract organizer/company
            organizer_elem = card.find('div', class_='event-card__organizer')
            company = self._clean_text(organizer_elem.get_text()) if organizer_elem else "Event Organizer"
            
            # Extract description
            desc_elem = card.find('div', class_='event-card__description')
            description = self._clean_text(desc_elem.get_text()) if desc_elem else ""
            
            # Extract date and time
            date_elem = card.find('div', class_='event-card__date')
            posted_date = None
            deadline = None
            if date_elem:
                date_text = self._clean_text(date_elem.get_text())
                posted_date = self._parse_date(date_text)
                # Set deadline to event date
                deadline = posted_date
            
            # Extract location
            location_elem = card.find('div', class_='event-card__location')
            location = self._clean_text(location_elem.get_text()) if location_elem else "Online"
            
            # Extract price/prize information
            price_elem = card.find('div', class_='event-card__price')
            prize_info = self._clean_text(price_elem.get_text()) if price_elem else ""
            
            # Extract skills from description and title
            skills = self._extract_skills(f"{title} {description}")
            
            return Opportunity(
                id=f"eventbrite_{event_id}",
                title=title,
                company=company,
                description=description,
                location=location,
                type=OpportunityType.HACKATHON,
                url=event_url,
                posted_date=posted_date,
                deadline=deadline,
                skills_required=skills,
                salary_range=prize_info,  # Use prize info as salary range
                experience_level="Any",
                remote="online" in location.lower() or "virtual" in location.lower(),
                source="eventbrite",
                raw_data={
                    'event_id': event_id,
                    'title': title,
                    'company': company,
                    'location': location,
                    'description': description,
                    'prize_info': prize_info
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing Eventbrite event card: {e}")
            return None


class HackerEarthHackathonScraper(SeleniumScraper):
    """Scraper for HackerEarth hackathon events using Selenium."""
    
    def __init__(self):
        super().__init__("https://www.hackerearth.com", delay_range=(3, 6))
        self.opportunity_type = OpportunityType.HACKATHON
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch hackathon opportunities from HackerEarth.
        
        Args:
            limit: Maximum number of opportunities to fetch
            **kwargs: Additional parameters (keywords, location, etc.)
            
        Returns:
            List of Opportunity objects
        """
        if not self.driver:
            logger.error("Selenium driver not available for HackerEarth scraping")
            return []
        
        try:
            # Navigate to hackathons page
            hackathons_url = f"{self.base_url}/challenges/hackathons/"
            logger.info(f"Scraping HackerEarth hackathons from: {hackathons_url}")
            
            self.driver.get(hackathons_url)
            
            # Wait for hackathons to load
            if not self._wait_for_element(By.CLASS_NAME, "challenge-card", timeout=15):
                logger.error("Failed to load HackerEarth hackathons page")
                return []
            
            opportunities = []
            processed_hackathons = set()
            
            # Scroll to load more hackathons
            self._scroll_to_bottom(pause_time=2.0)
            
            # Find all hackathon cards
            hackathon_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.challenge-card")
            
            for card in hackathon_cards:
                if len(opportunities) >= limit:
                    break
                
                try:
                    opportunity = self._parse_hackerearth_hackathon_card(card)
                    if opportunity and opportunity.id not in processed_hackathons:
                        opportunities.append(opportunity)
                        processed_hackathons.add(opportunity.id)
                except Exception as e:
                    logger.error(f"Error parsing HackerEarth hackathon card: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(opportunities)} hackathons from HackerEarth")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping HackerEarth: {e}")
            return []
        finally:
            self.close()
    
    def _parse_hackerearth_hackathon_card(self, card) -> Optional[Opportunity]:
        """Parse a HackerEarth hackathon card element into an Opportunity object."""
        try:
            # Extract hackathon link
            hackathon_link = card.find_element(By.CSS_SELECTOR, "a")
            hackathon_url = hackathon_link.get_attribute("href")
            hackathon_id = hackathon_url.split('/')[-2] if hackathon_url else ""
            
            # Extract title
            title_elem = card.find_element(By.CSS_SELECTOR, "h3.challenge-card-title")
            title = self._clean_text(title_elem.text)
            
            # Extract organizer/company
            company_elem = card.find_element(By.CSS_SELECTOR, "div.challenge-card-company")
            company = self._clean_text(company_elem.text)
            
            # Extract description
            description = ""
            try:
                desc_elem = card.find_element(By.CSS_SELECTOR, "div.challenge-card-description")
                description = self._clean_text(desc_elem.text)
            except NoSuchElementException:
                pass
            
            # Extract duration
            duration = ""
            try:
                duration_elem = card.find_element(By.CSS_SELECTOR, "div.challenge-card-duration")
                duration = self._clean_text(duration_elem.text)
            except NoSuchElementException:
                pass
            
            # Extract prize information
            prize_info = ""
            try:
                prize_elem = card.find_element(By.CSS_SELECTOR, "div.challenge-card-prize")
                prize_info = self._clean_text(prize_elem.text)
            except NoSuchElementException:
                pass
            
            # Extract skills from description and title
            skills = self._extract_skills(f"{title} {description}")
            
            # Extract dates
            posted_date = datetime.now() - timedelta(days=1)
            deadline = None
            try:
                date_elem = card.find_element(By.CSS_SELECTOR, "div.challenge-card-date")
                date_text = self._clean_text(date_elem.text)
                deadline = self._parse_date(date_text)
            except NoSuchElementException:
                pass
            
            return Opportunity(
                id=f"hackerearth_{hackathon_id}",
                title=title,
                company=company,
                description=description,
                location="Online",  # HackerEarth hackathons are typically online
                type=OpportunityType.HACKATHON,
                url=hackathon_url,
                posted_date=posted_date,
                deadline=deadline,
                skills_required=skills,
                salary_range=prize_info,
                experience_level="Any",
                remote=True,  # HackerEarth hackathons are typically online
                source="hackerearth",
                raw_data={
                    'hackathon_id': hackathon_id,
                    'title': title,
                    'company': company,
                    'description': description,
                    'duration': duration,
                    'prize_info': prize_info
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing HackerEarth hackathon card: {e}")
            return None


class UnstopHackathonScraper(BaseWebScraper):
    """Scraper for Unstop hackathon events."""
    
    def __init__(self):
        super().__init__("https://unstop.com", delay_range=(2, 4))
        self.opportunity_type = OpportunityType.HACKATHON
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch hackathon opportunities from Unstop.
        
        Args:
            limit: Maximum number of opportunities to fetch
            **kwargs: Additional parameters (keywords, location, etc.)
            
        Returns:
            List of Opportunity objects
        """
        try:
            keywords = kwargs.get('keywords', ['hackathon'])
            location = kwargs.get('location', '')
            
            # Build search URL for hackathons
            search_params = {
                'q': ' '.join(keywords) if isinstance(keywords, list) else keywords,
                'location': location,
                'type': 'hackathon',
                'sort': 'newest'
            }
            
            search_url = f"{self.base_url}/hackathons?{urlencode(search_params)}"
            logger.info(f"Scraping Unstop hackathons from: {search_url}")
            
            opportunities = []
            page = 1
            
            while len(opportunities) < limit and page <= 5:  # Limit to 5 pages
                page_url = f"{search_url}&page={page}"
                response = self._make_request(page_url)
                
                if not response:
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                hackathon_cards = soup.find_all('div', class_='hackathon-card')
                
                if not hackathon_cards:
                    logger.info("No more hackathon cards found, stopping pagination")
                    break
                
                for card in hackathon_cards:
                    if len(opportunities) >= limit:
                        break
                    
                    try:
                        opportunity = self._parse_unstop_hackathon_card(card)
                        if opportunity:
                            opportunities.append(opportunity)
                    except Exception as e:
                        logger.error(f"Error parsing Unstop hackathon card: {e}")
                        continue
                
                page += 1
                time.sleep(self._get_random_delay())
            
            logger.info(f"Successfully scraped {len(opportunities)} hackathons from Unstop")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping Unstop: {e}")
            return []
    
    def _parse_unstop_hackathon_card(self, card) -> Optional[Opportunity]:
        """Parse an Unstop hackathon card element into an Opportunity object."""
        try:
            # Extract hackathon link
            hackathon_link = card.find('a', href=True)
            if not hackathon_link:
                return None
            
            hackathon_url = urljoin(self.base_url, hackathon_link['href'])
            hackathon_id = hackathon_url.split('/')[-1]
            
            # Extract title
            title_elem = card.find('h3', class_='hackathon-title')
            title = self._clean_text(title_elem.get_text()) if title_elem else "Hackathon Event"
            
            # Extract organizer/company
            organizer_elem = card.find('div', class_='hackathon-organizer')
            company = self._clean_text(organizer_elem.get_text()) if organizer_elem else "Hackathon Organizer"
            
            # Extract description
            desc_elem = card.find('div', class_='hackathon-description')
            description = self._clean_text(desc_elem.get_text()) if desc_elem else ""
            
            # Extract location
            location_elem = card.find('div', class_='hackathon-location')
            location = self._clean_text(location_elem.get_text()) if location_elem else "Online"
            
            # Extract prize information
            prize_elem = card.find('div', class_='hackathon-prize')
            prize_info = self._clean_text(prize_elem.get_text()) if prize_elem else ""
            
            # Extract duration
            duration_elem = card.find('div', class_='hackathon-duration')
            duration = self._clean_text(duration_elem.get_text()) if duration_elem else ""
            
            # Extract dates
            date_elem = card.find('div', class_='hackathon-date')
            posted_date = None
            deadline = None
            if date_elem:
                date_text = self._clean_text(date_elem.get_text())
                posted_date = self._parse_date(date_text)
                deadline = posted_date
            
            # Extract skills from description and title
            skills = self._extract_skills(f"{title} {description}")
            
            return Opportunity(
                id=f"unstop_{hackathon_id}",
                title=title,
                company=company,
                description=description,
                location=location,
                type=OpportunityType.HACKATHON,
                url=hackathon_url,
                posted_date=posted_date,
                deadline=deadline,
                skills_required=skills,
                salary_range=prize_info,
                experience_level="Any",
                remote="online" in location.lower() or "virtual" in location.lower(),
                source="unstop",
                raw_data={
                    'hackathon_id': hackathon_id,
                    'title': title,
                    'company': company,
                    'location': location,
                    'description': description,
                    'prize_info': prize_info,
                    'duration': duration
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing Unstop hackathon card: {e}")
            return None


class InternshalaInternshipScraper(BaseWebScraper):
    """Scraper for Internshala internship opportunities."""
    
    def __init__(self):
        super().__init__("https://internshala.com", delay_range=(2, 4))
        self.opportunity_type = OpportunityType.INTERNSHIP
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch internship opportunities from Internshala.
        
        Args:
            limit: Maximum number of opportunities to fetch
            **kwargs: Additional parameters (keywords, location, etc.)
            
        Returns:
            List of Opportunity objects
        """
        try:
            keywords = kwargs.get('keywords', ['software development'])
            location = kwargs.get('location', '')
            
            # Build search URL for internships
            search_params = {
                'keywords': ' '.join(keywords) if isinstance(keywords, list) else keywords,
                'location': location,
                'category': '6',  # Technology category
                'sort': 'newest'
            }
            
            search_url = f"{self.base_url}/internships?{urlencode(search_params)}"
            logger.info(f"Scraping Internshala internships from: {search_url}")
            
            opportunities = []
            page = 1
            
            while len(opportunities) < limit and page <= 5:  # Limit to 5 pages
                page_url = f"{search_url}&page={page}"
                response = self._make_request(page_url)
                
                if not response:
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                internship_cards = soup.find_all('div', class_='internship_meta')
                
                if not internship_cards:
                    logger.info("No more internship cards found, stopping pagination")
                    break
                
                for card in internship_cards:
                    if len(opportunities) >= limit:
                        break
                    
                    try:
                        opportunity = self._parse_internshala_internship_card(card)
                        if opportunity:
                            opportunities.append(opportunity)
                    except Exception as e:
                        logger.error(f"Error parsing Internshala internship card: {e}")
                        continue
                
                page += 1
                time.sleep(self._get_random_delay())
            
            logger.info(f"Successfully scraped {len(opportunities)} internships from Internshala")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping Internshala: {e}")
            return []
    
    def _parse_internshala_internship_card(self, card) -> Optional[Opportunity]:
        """Parse an Internshala internship card element into an Opportunity object."""
        try:
            # Extract internship link
            internship_link = card.find('a', href=True)
            if not internship_link:
                return None
            
            internship_url = urljoin(self.base_url, internship_link['href'])
            internship_id = internship_url.split('/')[-1]
            
            # Extract title
            title_elem = card.find('h4', class_='internship_meta')
            title = self._clean_text(title_elem.get_text()) if title_elem else "Internship Opportunity"
            
            # Extract company
            company_elem = card.find('h4', class_='company_name')
            company = self._clean_text(company_elem.get_text()) if company_elem else "Unknown Company"
            
            # Extract location
            location_elem = card.find('div', class_='internship_meta')
            location = self._clean_text(location_elem.get_text()) if location_elem else "Remote"
            
            # Extract description
            desc_elem = card.find('div', class_='internship_meta')
            description = self._clean_text(desc_elem.get_text()) if desc_elem else ""
            
            # Extract stipend
            stipend_elem = card.find('span', class_='stipend')
            stipend = self._clean_text(stipend_elem.get_text()) if stipend_elem else ""
            
            # Extract duration
            duration_elem = card.find('div', class_='internship_meta')
            duration = self._clean_text(duration_elem.get_text()) if duration_elem else ""
            
            # Extract skills from description and title
            skills = self._extract_skills(f"{title} {description}")
            
            return Opportunity(
                id=f"internshala_{internship_id}",
                title=title,
                company=company,
                description=description,
                location=location,
                type=OpportunityType.INTERNSHIP,
                url=internship_url,
                posted_date=datetime.now() - timedelta(days=1),
                deadline=datetime.now() + timedelta(days=30),  # Default deadline
                skills_required=skills,
                salary_range=stipend,
                experience_level="Entry-level",
                remote="remote" in location.lower() or "work from home" in location.lower(),
                source="internshala",
                raw_data={
                    'internship_id': internship_id,
                    'title': title,
                    'company': company,
                    'location': location,
                    'description': description,
                    'stipend': stipend,
                    'duration': duration
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing Internshala internship card: {e}")
            return None



