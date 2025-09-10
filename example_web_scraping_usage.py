#!/usr/bin/env python3
"""
Example script showing how to use the web scraping functionality.
This demonstrates how to fetch real opportunities from various platforms.
"""

import sys
import os
import logging
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.web_scraping_fetchers import get_web_scraping_fetcher
from src.models import OpportunityType

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function demonstrating web scraping usage."""
    logger.info("Nexora Web Scraping Example")
    logger.info("=" * 50)
    
    # Get the web scraping fetcher
    fetcher = get_web_scraping_fetcher()
    
    try:
        # Example 1: Fetch all types of opportunities
        logger.info("\n1. Fetching all opportunities...")
        all_opportunities = fetcher.fetch_all_opportunities(limit_per_source=3)
        logger.info(f"Found {len(all_opportunities)} total opportunities")
        
        # Example 2: Search for specific job keywords
        logger.info("\n2. Searching for Python developer jobs...")
        python_jobs = fetcher.fetch_jobs(
            limit=5, 
            keywords=['python', 'developer', 'software engineer'],
            location='remote'
        )
        logger.info(f"Found {len(python_jobs)} Python developer jobs")
        
        # Example 3: Search for hackathons
        logger.info("\n3. Searching for hackathons...")
        hackathons = fetcher.fetch_hackathons(
            limit=3,
            keywords=['hackathon', 'coding', 'programming']
        )
        logger.info(f"Found {len(hackathons)} hackathons")
        
        # Example 4: Search for internships
        logger.info("\n4. Searching for internships...")
        internships = fetcher.fetch_internships(
            limit=3,
            keywords=['software development', 'internship']
        )
        logger.info(f"Found {len(internships)} internships")
        
        # Example 5: Fetch by opportunity type
        logger.info("\n5. Fetching by opportunity type...")
        job_opportunities = fetcher.fetch_opportunities_by_type(OpportunityType.JOB, limit=3)
        hackathon_opportunities = fetcher.fetch_opportunities_by_type(OpportunityType.HACKATHON, limit=3)
        internship_opportunities = fetcher.fetch_opportunities_by_type(OpportunityType.INTERNSHIP, limit=3)
        
        logger.info(f"Jobs: {len(job_opportunities)}")
        logger.info(f"Hackathons: {len(hackathon_opportunities)}")
        logger.info(f"Internships: {len(internship_opportunities)}")
        
        # Display some sample results
        logger.info("\n" + "=" * 50)
        logger.info("SAMPLE OPPORTUNITIES")
        logger.info("=" * 50)
        
        for i, opp in enumerate(all_opportunities[:5]):
            logger.info(f"\n{i+1}. {opp.title}")
            logger.info(f"   Company: {opp.company}")
            logger.info(f"   Type: {opp.type.value}")
            logger.info(f"   Location: {opp.location}")
            logger.info(f"   Skills: {', '.join(opp.skills_required[:3])}")
            logger.info(f"   URL: {opp.url}")
            if opp.salary_range:
                logger.info(f"   Salary: {opp.salary_range}")
        
        logger.info("\n" + "=" * 50)
        logger.info("Web scraping example completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during web scraping example: {e}")
        raise
    
    finally:
        # Cleanup resources
        try:
            fetcher.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


if __name__ == "__main__":
    main()



