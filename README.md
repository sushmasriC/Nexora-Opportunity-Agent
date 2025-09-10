# 🚀 Nexora AI Agent

An intelligent AI agent that automatically finds job opportunities, internships, and hackathons tailored to your profile using advanced embeddings, similarity matching, real-time web scraping, and API integrations.

## ✨ Features

- **🤖 AI-Powered Matching**: Uses Cohere embeddings for intelligent opportunity matching
- **🕷️ Hybrid Data Fetching**: Combines real-time web scraping with API integrations
- **📊 Multi-Source Data**: Fetches from Indeed, LinkedIn, Wellfound, Greenhouse, Eventbrite, HackerEarth, Internshala, and Unstop
- **🔌 API Integration**: Uses Apify and RapidAPI for reliable data access
- **📧 Email Notifications**: Sends personalized opportunity summaries via SendGrid
- **🎯 Smart Filtering**: Matches opportunities based on skills, interests, and preferences
- **⚡ Real-time Processing**: Fast matching and notification system
- **🔒 Descope Authentication**: Complete user authentication and authorization
- **👥 User Management**: Full user registration, profiles, and preferences
- **⏰ Automated Scheduling**: Hourly updates with background task processing
- **🗄️ Database Storage**: SQLite database for user data and profiles
- **🌐 REST API**: Complete FastAPI backend with Swagger documentation
- **🌐 Modern Frontend**: React-based web interface with beautiful UI

## 📺 Demo Video

Watch the Nexora AI Agent in action:

[![Nexora AI Agent Demo](https://img.youtube.com/vi/p4fYeixPFeA/0.jpg)](https://youtu.be/p4fYeixPFeA?si=LHBBlOOrzWe9bRSD)

[**Watch on YouTube**](https://youtu.be/p4fYeixPFeA?si=LHBBlOOrzWe9bRSD)

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Profile  │───▶│  Descope Auth    │───▶│  Nexora Agent   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  User Management │    │  Opportunities  │
                       │  (Profiles, Prefs)│    │  (Jobs, Hackathons)│
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Data Sources    │    │  AI Matching    │
                       │  ┌─────────────┐ │    │  (Cohere Embeddings)│
                       │  │Web Scrapers │ │    └─────────────────┘
                       │  │(Indeed, etc)│ │             │
                       │  └─────────────┘ │             ▼
                       │  ┌─────────────┐ │    ┌─────────────────┐
                       │  │API Services │ │    │  Email Notifications│
                       │  │(Apify, etc) │ │    │  (SendGrid)     │
                       │  └─────────────┘ │    └─────────────────┘
                       └──────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: Python 3.8+ with FastAPI
- **Frontend**: React 18 with TypeScript and Material-UI
- **AI/ML**: Cohere (embeddings & similarity)
- **Web Scraping**: BeautifulSoup4, Selenium, requests-html
- **API Integration**: Apify, RapidAPI
- **Orchestration**: LangChain
- **Email**: SendGrid
- **Authentication**: Descope (fully integrated)
- **Data Sources**: Hybrid approach - web scraping + API integration from Indeed, LinkedIn, Wellfound, Greenhouse, Eventbrite, HackerEarth, Internshala, Unstop
- **Caching**: Redis (with local fallback)
- **Database**: SQLite for user data



## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd nexora-agent

# Backend setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install  # or pnpm install
cd ..
```

### 2. Configure Environment

```bash
# Copy the environment template
cp env.template .env

# Edit .env with your API keys
nano .env  # or use your preferred editor
```

Fill in your API keys in the `.env` file:

```env
# Redis Configuration (optional - will fallback to local cache if not available)
REDIS_URL=redis://localhost:6379

# AI/ML APIs
COHERE_API_KEY=your_cohere_api_key_here

# Authentication (if needed)
DESCOPE_PROJECT_ID=your_descope_project_id
DESCOPE_API_KEY=your_descope_api_key

# Email Configuration
SENDGRID_API_KEY=your_sendgrid_api_key
EMAIL_SENDER=your_email@example.com
EMAIL_PASSWORD=your_email_password

# Web Scraping Configuration
WEB_SCRAPING_ENABLED=true
WEB_SCRAPING_DELAY_MIN=1.0
WEB_SCRAPING_DELAY_MAX=3.0
WEB_SCRAPING_TIMEOUT=30
WEB_SCRAPING_MAX_RETRIES=3

# Selenium Configuration
SELENIUM_HEADLESS=true
SELENIUM_WINDOW_SIZE=1920,1080
SELENIUM_DRIVER_PATH=  # Optional custom driver path

# API Integration (Optional - for reliable data access)
# Apify API Keys
WELLFOUND_API_TOKEN=your_apify_token
WELLFOUND_ACTOR_ID=your_actor_id
GREENHOUSE_API_TOKEN=your_apify_token
GREENHOUSE_ACTOR_ID=your_actor_id
LINKEDIN_API_TOKEN=your_apify_token
LINKEDIN_ACTOR_ID=your_actor_id

# RapidAPI Keys
INDEED_API_KEY=your_rapidapi_key
HACKEREARTH_API_KEY=your_rapidapi_key
```

### 3. Run the Application

#### Backend (API Server)
```bash
python run_api.py
```

#### Frontend (Web Interface)
```bash
cd frontend
npm start  # or pnpm start
```



### 4. Test Web Scraping

```bash
# Test the web scraping functionality
python test_web_scraping.py

# Run example usage
python example_web_scraping_usage.py
```

## 📁 Project Structure

```
nexora-agent/
├── src/                        # Backend Python code
│   ├── __init__.py
│   ├── agent.py                # Main Nexora agent class
│   ├── config.py               # Configuration management
│   ├── models.py               # Data models (Pydantic)
│   ├── scheduler.py            # Automated scheduling system
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py             # FastAPI REST endpoints
│   ├── database/
│   │   ├── __init__.py
│   │   └── user_db.py          # User database management
│   └── services/
│       ├── __init__.py
│       ├── auth_service.py     # Descope authentication
│       ├── cache_service.py    # Redis/local caching
│       ├── cohere_service.py   # Cohere embeddings service
│       ├── email_service.py    # SendGrid email service
│       ├── matching_engine.py  # AI matching logic
│       ├── opportunity_fetchers.py  # Data source fetchers
│       ├── web_scraping_service.py  # Web scraping infrastructure
│       ├── job_board_scrapers.py    # Job board scrapers
│       ├── hackathon_scrapers.py    # Hackathon platform scrapers
│       ├── web_scraping_fetchers.py # Main web scraping interface
│       └── apify_fetchers.py   # Legacy API integrations
├── frontend/                   # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   ├── contexts/          # React contexts
│   │   └── config/            # Frontend configuration
│   ├── package.json
│   └── tsconfig.json
├── main.py                     # Demo entry point
├── run_api.py                  # API server startup
├── test_web_scraping.py        # Web scraping tests
├── example_web_scraping_usage.py # Usage examples
├── requirements.txt            # Python dependencies
├── env.template               # Environment variables template
├── WEB_SCRAPING_README.md     # Web scraping documentation
└── README.md                  # This file
```

## 🕷️ Data Fetching Strategy

### Hybrid Approach: Web Scraping + API Integration
We use a **hybrid approach** that combines real-time web scraping with reliable API integrations for maximum data coverage and reliability.

### Supported Platforms

#### Web Scraping (Primary Method)
- **Job Boards**: Indeed, LinkedIn, Wellfound, Greenhouse
- **Hackathon Platforms**: Eventbrite, HackerEarth, Unstop
- **Internship Platforms**: Internshala

#### API Integration (Fallback Method)
- **Apify Services**: Wellfound, Greenhouse, LinkedIn, Eventbrite
- **RapidAPI Services**: Indeed, HackerEarth
- **Direct APIs**: Custom integrations where available

### Scraping Methods
- **BeautifulSoup**: For static content (Indeed, Wellfound, Eventbrite, Unstop, Internshala)
- **Selenium**: For dynamic content (LinkedIn, HackerEarth)
- **Rate Limiting**: Respectful scraping with configurable delays
- **Error Handling**: Graceful fallback to API services when scraping fails

### Web Scraping Configuration
```env
# Enable/disable web scraping
WEB_SCRAPING_ENABLED=true

# Rate limiting settings
WEB_SCRAPING_DELAY_MIN=1.0
WEB_SCRAPING_DELAY_MAX=3.0

# Timeout and retry settings
WEB_SCRAPING_TIMEOUT=30
WEB_SCRAPING_MAX_RETRIES=3

# Selenium browser settings
SELENIUM_HEADLESS=true
SELENIUM_WINDOW_SIZE=1920,1080
```

## 🔧 API Integration

### Cohere Setup
1. Sign up at [cohere.ai](https://cohere.ai/)
2. Get your API key from the dashboard
3. Add it to your `.env` file

### SendGrid Setup
1. Sign up at [sendgrid.com](https://sendgrid.com/)
2. Create an API key with "Mail Send" permissions
3. Add it to your `.env` file
4. Verify your sender email address

### Descope Setup (Required for Authentication)
1. Sign up at [descope.com](https://descope.com/)
2. Create a new project
3. Get your Project ID and API Key
4. Add them to your `.env` file
5. Configure authentication flows in Descope dashboard



## 🔍 How It Works

### 1. Hybrid Data Fetching
- **Primary Method**: Real-time web scraping from job boards and hackathon platforms
- **Fallback Method**: API integration (Apify, RapidAPI) when scraping fails
- **Multiple Techniques**: BeautifulSoup for static content, Selenium for dynamic content
- **Rate Limiting**: Respectful scraping with configurable delays to avoid being blocked
- **Error Handling**: Graceful fallback to API services if scraping fails
- **Data Normalization**: Converts all data sources into consistent format

### 2. User Authentication
- **Descope Integration**: Complete user authentication and authorization
- **JWT Tokens**: Secure session management
- **User Profiles**: Personalized user data and preferences
- **Role-based Access**: Different access levels for different user types

### 3. AI Matching
- Creates embeddings for both user profiles and opportunities using Cohere
- Calculates semantic similarity between profiles and opportunities
- Considers skill overlap, interest alignment, and location preferences
- Ranks matches by weighted similarity score

### 4. Frontend Interface
- **React Dashboard**: Modern web interface for viewing recommendations
- **Profile Management**: User-friendly profile editing and preferences
- **Real-time Updates**: Live data from hybrid fetching approach
- **Responsive Design**: Works on desktop and mobile devices

### 5. Email Notifications
- Generates beautiful HTML emails with matched opportunities
- Includes match reasoning and similarity scores
- Sends personalized summaries via SendGrid

## 🧪 Testing

The project includes comprehensive testing functionality:

```bash
# Test web scraping functionality
python test_web_scraping.py

# Run web scraping examples
python example_web_scraping_usage.py

# Run the full demo
python main.py

# Start the complete application
python run_api.py  # Backend
cd frontend && npm start  # Frontend
```

### Test Coverage
- **Web Scraping Tests**: Verify all scrapers work correctly
- **API Tests**: Test all REST endpoints
- **Frontend Tests**: React component testing
- **Integration Tests**: End-to-end workflow testing

## 🔮 Future Enhancements

- [x] **Real-time Web Scraping**: ✅ Implemented comprehensive web scraping system
- [x] **Modern Frontend**: ✅ Built React-based web interface
- [x] **User Management**: ✅ Complete user profiles and preferences
- [x] **Automated Scheduling**: ✅ Hourly updates with background processing
- [ ] **Advanced Analytics**: Enhanced user engagement tracking
- [ ] **Mobile App**: Create mobile notifications
- [ ] **Social Features**: Add sharing and collaboration features
- [ ] **More Platforms**: Add additional job boards and hackathon platforms
- [ ] **Caching Optimization**: Improve performance with better caching
- [ ] **Proxy Support**: Add proxy rotation for better scraping reliability




**Built with ❤️ for the developer community**

*Nexora AI Agent - Your intelligent opportunity finder with real-time web scraping* 🚀🕷️
