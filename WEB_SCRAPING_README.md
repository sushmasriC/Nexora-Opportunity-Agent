# Web Scraping Implementation for Nexora AI Agent

This document describes the web scraping implementation that replaces API-based and mock data fetching with real-time data scraping from various job boards and hackathon platforms.

## Overview

The web scraping system provides a comprehensive solution for fetching real opportunities from multiple sources:

- **Job Boards**: Indeed, LinkedIn, Wellfound (AngelList), Greenhouse
- **Hackathon Platforms**: Eventbrite, HackerEarth, Unstop
- **Internship Platforms**: Internshala

## Architecture

### Core Components

1. **Base Web Scraper** (`src/services/web_scraping_service.py`)
   - Abstract base class for all scrapers
   - Common utilities for date parsing, skill extraction, text cleaning
   - Rate limiting and error handling

2. **Selenium Scraper** (`src/services/web_scraping_service.py`)
   - Base class for JavaScript-heavy sites
   - Handles dynamic content loading
   - Automatic scrolling and element waiting

3. **Job Board Scrapers** (`src/services/job_board_scrapers.py`)
   - IndeedScraper: Uses BeautifulSoup for static content
   - LinkedInScraper: Uses Selenium for dynamic content
   - WellfoundScraper: Uses BeautifulSoup for static content
   - GreenhouseScraper: Uses BeautifulSoup for static content

4. **Hackathon Scrapers** (`src/services/hackathon_scrapers.py`)
   - EventbriteHackathonScraper: Scrapes hackathon events
   - HackerEarthHackathonScraper: Uses Selenium for dynamic content
   - UnstopHackathonScraper: Scrapes hackathon competitions
   - InternshalaInternshipScraper: Scrapes internship opportunities

5. **Web Scraping Fetchers** (`src/services/web_scraping_fetchers.py`)
   - Main interface for fetching opportunities
   - Coordinates multiple scrapers
   - Provides fallback to legacy fetchers

## Configuration

Add the following environment variables to your `.env` file:

```env
# Web Scraping Configuration
WEB_SCRAPING_ENABLED=true
WEB_SCRAPING_DELAY_MIN=1.0
WEB_SCRAPING_DELAY_MAX=3.0
WEB_SCRAPING_TIMEOUT=30
WEB_SCRAPING_MAX_RETRIES=3
WEB_SCRAPING_USER_AGENT=  # Optional custom user agent
WEB_SCRAPING_PROXY=  # Optional proxy configuration

# Selenium Configuration
SELENIUM_HEADLESS=true
SELENIUM_WINDOW_SIZE=1920,1080
SELENIUM_DRIVER_PATH=  # Optional custom driver path
```

## Dependencies

The following packages are required for web scraping:

```
beautifulsoup4==4.12.2
selenium==4.15.2
requests-html==0.10.0
lxml==4.9.3
fake-useragent==1.4.0
```

Install them using:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from src.services.web_scraping_fetchers import get_web_scraping_fetcher
from src.models import OpportunityType

# Get the fetcher
fetcher = get_web_scraping_fetcher()

# Fetch all opportunities
all_opportunities = fetcher.fetch_all_opportunities(limit_per_source=10)

# Fetch specific types
jobs = fetcher.fetch_jobs(limit=20, keywords=['python', 'developer'])
hackathons = fetcher.fetch_hackathons(limit=10, keywords=['hackathon'])
internships = fetcher.fetch_internships(limit=15, keywords=['software development'])

# Fetch by opportunity type
job_opportunities = fetcher.fetch_opportunities_by_type(OpportunityType.JOB, limit=20)
```

### Advanced Usage

```python
# Search with specific parameters
jobs = fetcher.fetch_jobs(
    limit=10,
    keywords=['machine learning', 'AI', 'data scientist'],
    location='San Francisco'
)

# Fetch from specific sources
indeed_scraper = IndeedScraper()
indeed_jobs = indeed_scraper.fetch_opportunities(
    limit=5,
    keywords=['python developer'],
    location='remote'
)
```

## Features

### Rate Limiting
- Configurable delays between requests
- Random delays to avoid detection
- Respectful scraping practices

### Error Handling
- Comprehensive error handling and logging
- Fallback to legacy fetchers if web scraping fails
- Graceful degradation

### Data Extraction
- Automatic skill extraction from job descriptions
- Date parsing for various formats
- Text cleaning and normalization
- Experience level detection

### Browser Automation
- Selenium integration for JavaScript-heavy sites
- Headless browser support
- Automatic scrolling and content loading
- Element waiting and interaction

## Testing

Run the test suite to verify web scraping functionality:

```bash
python test_web_scraping.py
```

Run the example script to see web scraping in action:

```bash
python example_web_scraping_usage.py
```

## Scraper-Specific Notes

### Indeed Scraper
- Uses BeautifulSoup for static content
- Handles pagination automatically
- Extracts job details from search results

### LinkedIn Scraper
- Uses Selenium for dynamic content
- Requires Chrome/Chromium browser
- Handles infinite scrolling

### Wellfound Scraper
- Uses BeautifulSoup for static content
- Scrapes startup job listings
- Handles pagination

### Greenhouse Scraper
- Scrapes from multiple company pages
- Uses BeautifulSoup for static content
- Handles various company layouts

### Eventbrite Scraper
- Scrapes hackathon events
- Uses BeautifulSoup for static content
- Filters for technology events

### HackerEarth Scraper
- Uses Selenium for dynamic content
- Scrapes coding competitions
- Handles infinite scrolling

### Unstop Scraper
- Scrapes hackathon competitions
- Uses BeautifulSoup for static content
- Handles pagination

### Internshala Scraper
- Scrapes internship opportunities
- Uses BeautifulSoup for static content
- Handles pagination

## Troubleshooting

### Common Issues

1. **Selenium Driver Issues**
   - Ensure Chrome/Chromium is installed
   - Check SELENIUM_DRIVER_PATH configuration
   - Verify SELENIUM_HEADLESS setting

2. **Rate Limiting**
   - Increase delay settings if getting blocked
   - Use proxy configuration if needed
   - Check website terms of service

3. **Parsing Errors**
   - Websites may change their structure
   - Update CSS selectors if needed
   - Check logs for specific errors

### Debugging

Enable debug logging to see detailed scraping information:

```python
import logging
logging.getLogger('src.services').setLevel(logging.DEBUG)
```

## Legal Considerations

- Respect website terms of service
- Use appropriate delays between requests
- Don't overload servers with too many requests
- Consider using official APIs when available
- Follow robots.txt guidelines

## Performance

- Web scraping is slower than API calls
- Consider caching results
- Use appropriate limits to avoid timeouts
- Monitor memory usage with Selenium

## Future Enhancements

- Add more job boards and platforms
- Implement caching mechanisms
- Add proxy rotation support
- Improve error recovery
- Add data validation
- Implement monitoring and alerting



