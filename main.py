"""
Nexora AI Agent - Main Entry Point
Demonstrates the complete workflow: fetch opportunities, match with user profile, and send notifications.
"""

import logging
import sys
from datetime import datetime
from typing import Optional

# Add src to path for imports
sys.path.append('src')

from src.agent import NexoraAgent
from src.models import UserProfile, OpportunityType
from src.config import settings
from src.database.user_db import UserDatabase
from src.services.auth_service import AuthService
from src.scheduler import SchedulerManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('nexora.log')
    ]
)

logger = logging.getLogger(__name__)


def print_banner():
    """Print the Nexora AI Agent banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                    🚀 NEXORA AI AGENT 🚀                     ║
    ║                                                              ║
    ║              Automatic Opportunity Finder                     ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_separator(title: str = ""):
    """Print a separator with optional title."""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")


def create_demo_user_profile() -> UserProfile:
    """Create a demo user profile for testing."""
    return UserProfile(
        user_id="demo_user_001",
        email="demo@nexora.com",  # Change this to your email for testing
        skills=[
            "Python", "JavaScript", "React", "Node.js", "AWS", 
            "Machine Learning", "Data Science", "Docker", "Git",
            "MongoDB", "PostgreSQL", "REST APIs", "GraphQL"
        ],
        interests=[
            "Artificial Intelligence", "Web Development", "Startups", 
            "Open Source", "Tech Innovation", "Remote Work",
            "FinTech", "EdTech", "HealthTech", "Blockchain"
        ],
        experience_level="Mid-level",
        preferred_locations=["Remote", "Bangalore", "Hyderabad", "Mumbai"],
        remote_preference=True,
        resume_text="""
        Experienced software engineer with 4+ years in full-stack development.
        Passionate about AI/ML and building scalable web applications.
        Strong background in Python, JavaScript, React, and cloud technologies.
        Led multiple projects involving machine learning and data analysis.
        Experience with microservices architecture and DevOps practices.
        """
    )


def demo_opportunity_fetching(agent: NexoraAgent):
    """Demonstrate opportunity fetching from different sources."""
    print_separator("DEMO: Fetching Opportunities")
    
    # Fetch all opportunities
    print("🔍 Fetching opportunities from all sources...")
    all_opportunities = agent.fetch_opportunities(limit_per_source=10)
    print(f"✅ Fetched {len(all_opportunities)} total opportunities")
    
    # Show breakdown by type
    job_count = len([opp for opp in all_opportunities if opp.type == OpportunityType.JOB])
    intern_count = len([opp for opp in all_opportunities if opp.type == OpportunityType.INTERNSHIP])
    hack_count = len([opp for opp in all_opportunities if opp.type == OpportunityType.HACKATHON])
    
    print(f"   📊 Jobs: {job_count}")
    print(f"   📊 Internships: {intern_count}")
    print(f"   📊 Hackathons: {hack_count}")
    
    # Show breakdown by source
    sources = {}
    for opp in all_opportunities:
        sources[opp.source] = sources.get(opp.source, 0) + 1
    
    print(f"   📊 Sources: {dict(sources)}")
    
    # Show sample opportunities
    print(f"\n📋 Sample Opportunities:")
    for i, opp in enumerate(all_opportunities[:3]):
        print(f"   {i+1}. {opp.title} at {opp.company}")
        print(f"      Type: {opp.type.value} | Location: {opp.location}")
        print(f"      Skills: {', '.join(opp.skills_required[:3])}")
        print()
    
    return all_opportunities


def demo_matching_engine(agent: NexoraAgent, opportunities, user_profile: UserProfile):
    """Demonstrate the matching engine."""
    print_separator("DEMO: Matching Engine")
    
    print("🎯 Finding matches for user profile...")
    matches = agent.find_matches_for_user(
        user_profile, 
        opportunities, 
        min_score=0.3, 
        max_results=10
    )
    
    print(f"✅ Found {len(matches)} matches above threshold")
    
    if matches:
        # Show match statistics
        stats = agent.matching_engine.get_match_statistics(matches)
        print(f"\n📊 Match Statistics:")
        print(f"   Average Score: {stats['average_score']:.2%}")
        print(f"   Highest Score: {stats['highest_score']:.2%}")
        print(f"   Lowest Score: {stats['lowest_score']:.2%}")
        print(f"   By Type: {stats['by_type']}")
        print(f"   By Source: {stats['by_source']}")
        
        # Show top matches
        print(f"\n🏆 Top Matches:")
        for i, match in enumerate(matches[:5]):
            print(f"   {i+1}. {match.opportunity.title} at {match.opportunity.company}")
            print(f"      Score: {match.similarity_score:.2%} | Type: {match.opportunity.type.value}")
            print(f"      Matched Skills: {', '.join(match.matched_skills[:3])}")
            print(f"      Reasoning: {match.reasoning[:100]}...")
            print()
    
    return matches


def demo_email_service(agent: NexoraAgent, user_email: str):
    """Demonstrate email service."""
    print_separator("DEMO: Email Service")
    
    print(f"📧 Sending test email to {user_email}...")
    success = agent.send_test_email(user_email)
    
    if success:
        print("✅ Test email sent successfully!")
        print("   Check your inbox for the test email.")
    else:
        print("❌ Failed to send test email.")
        print("   Please check your SendGrid configuration.")
    
    return success


def demo_full_workflow(agent: NexoraAgent, user_profile: UserProfile):
    """Demonstrate the complete workflow."""
    print_separator("DEMO: Complete Workflow")
    
    print("🚀 Running complete workflow...")
    print("   This will: fetch opportunities → find matches → send email")
    
    result = agent.run_full_workflow(
        user_profile,
        limit_per_source=8,
        min_score=0.3,
        max_results=10
    )
    
    if result["success"]:
        print("✅ Workflow completed successfully!")
        print(f"   Duration: {result['duration_seconds']:.2f} seconds")
        print(f"   Opportunities fetched: {result['total_opportunities']}")
        print(f"   Matches found: {result['matches_found']}")
        print(f"   Email sent: {result['email_sent']}")
        
        # Show detailed statistics
        stats = result['match_statistics']
        print(f"\n📊 Detailed Statistics:")
        print(f"   Average match score: {stats['average_score']:.2%}")
        print(f"   Matches by type: {stats['by_type']}")
        print(f"   Matches by source: {stats['by_source']}")
    else:
        print("❌ Workflow failed!")
        print(f"   Error: {result['error']}")
    
    return result


def demo_profile_analysis(agent: NexoraAgent, user_profile: UserProfile):
    """Demonstrate user profile analysis."""
    print_separator("DEMO: Profile Analysis")
    
    print("🔍 Analyzing user profile...")
    analysis = agent.analyze_user_profile(user_profile)
    
    print("✅ Profile analysis completed!")
    print(f"\n📊 Profile Analysis Results:")
    print(f"   User ID: {analysis['user_id']}")
    print(f"   Skills: {analysis['skills_count']}")
    print(f"   Interests: {analysis['interests_count']}")
    print(f"   Preferred Locations: {analysis['preferred_locations_count']}")
    print(f"   Experience Level: {analysis['experience_level']}")
    print(f"   Remote Preference: {analysis['remote_preference']}")
    print(f"   Profile Completeness: {analysis['profile_completeness']:.1%}")
    print(f"   Recommended Types: {', '.join(analysis['recommended_opportunity_types'])}")
    
    return analysis


def main():
    """Main function to run the Nexora AI Agent demo."""
    print_banner()
    
    try:
        # Initialize the agent
        print("🔧 Initializing Nexora AI Agent...")
        agent = NexoraAgent()
        print("✅ Agent initialized successfully!")
        
        # Initialize additional services
        print("🔧 Initializing user database...")
        user_db = UserDatabase()
        print("✅ User database initialized!")
        
        print("🔧 Initializing authentication service...")
        auth_service = AuthService()
        print("✅ Authentication service initialized!")
        
        print("🔧 Initializing scheduler...")
        scheduler_manager = SchedulerManager()
        scheduler_manager.initialize(agent, user_db)
        print("✅ Scheduler initialized!")
        
        # Create demo user profile
        print("\n👤 Creating demo user profile...")
        user_profile = create_demo_user_profile()
        print("✅ Demo user profile created!")
        
        # Get user email for testing (optional)
        user_email = input(f"\n📧 Enter your email for testing (or press Enter to use demo email): ").strip()
        if not user_email:
            user_email = user_profile.email
            print(f"   Using demo email: {user_email}")
        else:
            user_profile.email = user_email
            print(f"   Using provided email: {user_email}")
        
        # Run demos
        print_separator("STARTING DEMONSTRATIONS")
        
        # Demo 1: Profile Analysis
        demo_profile_analysis(agent, user_profile)
        
        # Demo 2: Opportunity Fetching
        opportunities = demo_opportunity_fetching(agent)
        
        # Demo 3: Matching Engine
        matches = demo_matching_engine(agent, opportunities, user_profile)
        
        # Demo 4: Email Service
        email_success = demo_email_service(agent, user_email)
        
        # Demo 5: Complete Workflow (only if email service is working)
        if email_success:
            workflow_result = demo_full_workflow(agent, user_profile)
        else:
            print_separator("SKIPPING FULL WORKFLOW")
            print("⚠️  Skipping full workflow demo due to email service issues.")
            print("   Please check your SendGrid configuration and try again.")
        
        # Demo 6: Scheduler Status
        print_separator("DEMO: Scheduler Status")
        scheduler_status = scheduler_manager.get_status()
        print("📅 Scheduler Status:")
        print(f"   Running: {scheduler_status.get('scheduler_running', False)}")
        print(f"   Total Jobs: {scheduler_status.get('total_jobs', 0)}")
        if scheduler_status.get('jobs'):
            print("   Active Jobs:")
            for job in scheduler_status['jobs']:
                print(f"     - {job['name']} (Next: {job.get('next_run_time', 'N/A')})")
        
        # Demo 7: User Management
        print_separator("DEMO: User Management")
        print("👥 User Management Features:")
        print("   ✅ User registration and authentication")
        print("   ✅ Profile management and preferences")
        print("   ✅ Database storage and retrieval")
        print("   ✅ Session management")
        print("   ✅ REST API endpoints available")
        
        # Final summary
        print_separator("DEMO COMPLETED")
        print("🎉 Nexora AI Agent demonstration completed!")
        print("\n📋 What was demonstrated:")
        print("   ✅ Profile analysis and insights")
        print("   ✅ Opportunity fetching from multiple sources")
        print("   ✅ AI-powered matching using Cohere embeddings")
        print("   ✅ Email notification system")
        print("   ✅ User authentication and management")
        print("   ✅ Database storage and retrieval")
        print("   ✅ Automated scheduling system")
        print("   ✅ REST API endpoints")
        if email_success:
            print("   ✅ Complete end-to-end workflow")
        
        print(f"\n📝 Logs saved to: nexora.log")
        print(f"📧 Check your email ({user_email}) for notifications!")
        print(f"\n🚀 To start the API server, run: python run_api.py")
        print(f"📖 API documentation will be available at: http://localhost:8000/docs")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user.")
    except Exception as e:
        logger.error(f"Error in main demo: {e}")
        print(f"\n❌ Error occurred: {e}")
        print("   Check the logs for more details.")
    
    print(f"\n{'='*60}")
    print("Thank you for trying Nexora AI Agent! 🚀")


if __name__ == "__main__":
    main()
