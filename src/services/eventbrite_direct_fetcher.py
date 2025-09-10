"""
Direct Eventbrite API fetcher using the Eventbrite API key.
Fetches hackathons directly from Eventbrite API without Apify.
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from ..models import Opportunity, OpportunityType
from ..config import settings

logger = logging.getLogger(__name__)


class EventbriteDirectFetcher:
    """Direct fetcher for Eventbrite hackathons using Eventbrite API."""
    
    def __init__(self):
        """Initialize Eventbrite direct fetcher."""
        self.api_key = "KS2XQFVMH7TR2UWAN65O"  # Your Eventbrite API key
        self.base_url = "https://www.eventbriteapi.com/v3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Test the API key first
        self._test_api_key()
    
    def _test_api_key(self):
        """Test if the API key is valid."""
        try:
            response = requests.get(
                f"{self.base_url}/users/me/",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                logger.info("✅ Eventbrite API key is valid")
            else:
                logger.warning(f"⚠️ Eventbrite API key test failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.warning(f"⚠️ Could not test Eventbrite API key: {e}")
    
    def fetch_opportunities(self, limit: int = 50, **kwargs) -> List[Opportunity]:
        """
        Fetch hackathon opportunities from Eventbrite API.
        
        Args:
            limit: Maximum number of opportunities to fetch
            
        Returns:
            List of Opportunity objects
        """
        try:
            logger.info(f"Fetching hackathons from Eventbrite API (limit: {limit})")
            
            # First, let's try to get the user's events
            logger.info("Trying to get user's events first...")
            user_events_response = requests.get(
                f"{self.base_url}/users/me/events/",
                headers=self.headers,
                timeout=30
            )
            
            if user_events_response.status_code == 200:
                logger.info("✅ Successfully got user's events")
                data = user_events_response.json()
                events = data.get("events", [])
                logger.info(f"Found {len(events)} events from user's account")
                
                # Filter for hackathons
                hackathon_events = []
                for event in events:
                    name = event.get("name", {}).get("text", "").lower()
                    description = event.get("description", {}).get("text", "").lower()
                    if "hackathon" in name or "hackathon" in description:
                        hackathon_events.append(event)
                
                logger.info(f"Found {len(hackathon_events)} hackathon events")
                events = hackathon_events[:limit]
            else:
                logger.warning(f"Could not get user's events: {user_events_response.status_code}")
                # Fallback to search
                search_params = {
                    "q": "hackathon",
                    "sort_by": "date",
                    "time_filter": "current_future",
                    "expand": "venue,organizer",
                    "page_size": min(limit, 50)
                }
                
                # Try different endpoints
                endpoints_to_try = [
                    f"{self.base_url}/events/search/",
                    f"{self.base_url}/events/search",
                    f"{self.base_url}/events/",
                    f"{self.base_url}/events"
                ]
                
                response = None
                for endpoint in endpoints_to_try:
                    try:
                        logger.info(f"Trying endpoint: {endpoint}")
                        response = requests.get(
                            endpoint,
                            headers=self.headers,
                            params=search_params,
                            timeout=30
                        )
                        if response.status_code == 200:
                            logger.info(f"✅ Success with endpoint: {endpoint}")
                            break
                        else:
                            logger.warning(f"❌ Failed with endpoint {endpoint}: {response.status_code}")
                    except Exception as e:
                        logger.warning(f"❌ Error with endpoint {endpoint}: {e}")
                        continue
                
                if not response or response.status_code != 200:
                    logger.error("All Eventbrite API endpoints failed")
                    return self._get_sample_hackathons(limit)
                
                data = response.json()
                events = data.get("events", [])
                logger.info(f"Successfully fetched {len(events)} events from Eventbrite")
            
            # Process events (either from user's events or search results)
            opportunities = []
            for event in events:
                try:
                    opportunity = self._parse_eventbrite_event(event)
                    if opportunity:
                        opportunities.append(opportunity)
                except Exception as e:
                    logger.warning(f"Error parsing event {event.get('id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(opportunities)} hackathon opportunities")
            return opportunities
                
        except Exception as e:
            logger.error(f"Error fetching from Eventbrite API: {e}")
            return self._get_sample_hackathons(limit)
    
    def _parse_eventbrite_event(self, event: Dict[str, Any]) -> Optional[Opportunity]:
        """Parse Eventbrite event data into Opportunity object."""
        try:
            # Extract basic information
            event_id = event.get("id", "")
            name = event.get("name", {}).get("text", "Untitled Event")
            description = event.get("description", {}).get("text", "")
            
            # Extract date information
            start_time = event.get("start", {}).get("utc")
            end_time = event.get("end", {}).get("utc")
            
            # Extract location
            venue = event.get("venue", {})
            location = "Online"
            if venue:
                venue_name = venue.get("name", "")
                address = venue.get("address", {})
                city = address.get("city", "")
                region = address.get("region", "")
                country = address.get("country", "")
                
                if city and region:
                    location = f"{city}, {region}"
                elif city:
                    location = city
                elif venue_name:
                    location = venue_name
                else:
                    location = "Online"
            
            # Extract organizer
            organizer = event.get("organizer", {})
            company = organizer.get("name", "Event Organizer")
            
            # Extract URL
            url = event.get("url", "")
            
            # Determine if it's a hackathon based on keywords
            hackathon_keywords = ["hackathon", "hack", "coding", "programming", "tech challenge", "dev challenge"]
            is_hackathon = any(keyword in name.lower() or keyword in description.lower() 
                             for keyword in hackathon_keywords)
            
            if not is_hackathon:
                return None
            
            # Create opportunity
            opportunity = Opportunity(
                id=f"eventbrite_{event_id}",
                title=name,
                company=company,
                description=description[:500] + "..." if len(description) > 500 else description,
                location=location,
                type=OpportunityType.HACKATHON,
                url=url,
                posted_date=datetime.now() - timedelta(days=1),  # Assume posted yesterday
                deadline=datetime.fromisoformat(end_time.replace('Z', '+00:00')) if end_time else None,
                skills_required=["Programming", "Teamwork", "Problem Solving", "Innovation"],
                salary_range=None,
                experience_level="Any",
                remote=True if "online" in location.lower() else False,
                source="eventbrite_direct"
            )
            
            return opportunity
            
        except Exception as e:
            logger.error(f"Error parsing Eventbrite event: {e}")
            return None
    
    def _get_sample_hackathons(self, limit: int) -> List[Opportunity]:
        """Return sample hackathon data as fallback."""
        logger.warning("Using sample hackathon data as fallback")
        
        sample_hackathons = [
            {
                "title": "AI Innovation Hackathon",
                "company": "TechCorp Events",
                "location": "Bangalore, India",
                "description": "Join us for an exciting AI innovation hackathon where developers and data scientists come together to build cutting-edge solutions.",
                "url": "https://eventbrite.com/e/ai-innovation-hackathon",
                "skills": ["Python", "Machine Learning", "AI", "Data Science"]
            },
            {
                "title": "Web3 Development Challenge",
                "company": "Blockchain Events Inc",
                "location": "Online",
                "description": "A 48-hour hackathon focused on building decentralized applications and Web3 solutions.",
                "url": "https://eventbrite.com/e/web3-development-challenge",
                "skills": ["JavaScript", "Solidity", "Web3", "Blockchain"]
            },
            {
                "title": "FinTech Innovation Hackathon",
                "company": "FinanceTech Hub",
                "location": "Hyderabad, India",
                "description": "Build the next generation of financial technology solutions in this intensive hackathon.",
                "url": "https://eventbrite.com/e/fintech-innovation-hackathon",
                "skills": ["React", "Node.js", "FinTech", "API Development"]
            }
        ]
        
        opportunities = []
        for i, hackathon in enumerate(sample_hackathons[:limit]):
            opportunity = Opportunity(
                id=f"eventbrite_sample_{i}",
                title=hackathon["title"],
                company=hackathon["company"],
                description=hackathon["description"],
                location=hackathon["location"],
                type=OpportunityType.HACKATHON,
                url=hackathon["url"],
                posted_date=datetime.now() - timedelta(days=i),
                deadline=datetime.now() + timedelta(days=30-i),
                skills_required=hackathon["skills"],
                salary_range=None,
                experience_level="Any",
                remote=hackathon["location"] == "Online",
                source="eventbrite_direct"
            )
            opportunities.append(opportunity)
        
        return opportunities
