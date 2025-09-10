"""
Weekly email service for Nexora AI Agent.
Handles weekly summary emails with personalized recommendations.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from apscheduler.triggers.cron import CronTrigger

from .email_service import EmailService
from .personalization_service import PersonalizationService
from ..database.user_db import UserDatabase

logger = logging.getLogger(__name__)


class WeeklyEmailService:
    """Service for sending weekly summary emails."""
    
    def __init__(self, email_service: EmailService, personalization_service: PersonalizationService, user_db: UserDatabase):
        """
        Initialize weekly email service.
        
        Args:
            email_service: EmailService instance
            personalization_service: PersonalizationService instance
            user_db: UserDatabase instance
        """
        self.email_service = email_service
        self.personalization_service = personalization_service
        self.user_db = user_db
    
    def create_weekly_summary_html(self, summary_data: Dict[str, Any]) -> str:
        """
        Create HTML content for weekly summary email.
        
        Args:
            summary_data: Weekly summary data
            
        Returns:
            HTML string for the weekly summary
        """
        user_name = summary_data.get('user_name', 'User')
        job_matches = summary_data.get('top_job_matches', [])
        hackathon_matches = summary_data.get('top_hackathon_matches', [])
        
        # Create job matches HTML
        job_matches_html = ""
        for i, match in enumerate(job_matches[:5]):
            job_matches_html += f"""
            <div style="border: 1px solid #e0e0e0; padding: 15px; margin: 10px 0; border-radius: 8px; background-color: #f9f9f9;">
                <h4 style="color: #2c3e50; margin-top: 0;">{i+1}. Job Match</h4>
                <p><strong>Similarity Score:</strong> {match['similarity_score']:.1%}</p>
                <p><strong>Matched Skills:</strong> {', '.join(match['matched_skills'][:3])}</p>
                <p><strong>Reasoning:</strong> {match['reasoning'][:150]}...</p>
                <a href="#" style="color: #007bff; text-decoration: none;">View Details →</a>
            </div>
            """
        
        # Create hackathon matches HTML
        hackathon_matches_html = ""
        for i, match in enumerate(hackathon_matches[:3]):
            hackathon_matches_html += f"""
            <div style="border: 1px solid #e0e0e0; padding: 15px; margin: 10px 0; border-radius: 8px; background-color: #f0f8ff;">
                <h4 style="color: #2c3e50; margin-top: 0;">{i+1}. Hackathon Match</h4>
                <p><strong>Similarity Score:</strong> {match['similarity_score']:.1%}</p>
                <p><strong>Matched Skills:</strong> {', '.join(match['matched_skills'][:3])}</p>
                <p><strong>Reasoning:</strong> {match['reasoning'][:150]}...</p>
                <a href="#" style="color: #007bff; text-decoration: none;">View Details →</a>
            </div>
            """
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Weekly Opportunity Summary - Nexora</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 28px;">📊 Weekly Summary</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px;">Your personalized opportunity digest</p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                <h2 style="color: #2c3e50; margin-top: 0;">Hello {user_name}! 👋</h2>
                <p>Here's your weekly summary of the best opportunities we found for you:</p>
                
                <div style="display: flex; justify-content: space-around; margin: 20px 0;">
                    <div style="text-align: center; background: white; padding: 15px; border-radius: 8px; flex: 1; margin: 0 10px;">
                        <h3 style="color: #27ae60; margin: 0;">{len(job_matches)}</h3>
                        <p style="margin: 5px 0 0 0;">Job Matches</p>
                    </div>
                    <div style="text-align: center; background: white; padding: 15px; border-radius: 8px; flex: 1; margin: 0 10px;">
                        <h3 style="color: #3498db; margin: 0;">{len(hackathon_matches)}</h3>
                        <p style="margin: 5px 0 0 0;">Hackathon Matches</p>
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 30px;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">💼 Top Job Matches</h2>
                {job_matches_html if job_matches_html else '<p style="text-align: center; color: #666; padding: 20px;">No new job matches this week. Check back next week!</p>'}
            </div>
            
            <div style="margin-bottom: 30px;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #e74c3c; padding-bottom: 10px;">🏆 Top Hackathon Matches</h2>
                {hackathon_matches_html if hackathon_matches_html else '<p style="text-align: center; color: #666; padding: 20px;">No new hackathon matches this week. Check back next week!</p>'}
            </div>
            
            <div style="background-color: #e8f5e8; padding: 20px; border-radius: 8px; margin: 30px 0;">
                <h3 style="color: #27ae60; margin-top: 0;">💡 Pro Tips</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Update your skills regularly to get better matches</li>
                    <li>Set your preferences to receive more relevant opportunities</li>
                    <li>Apply early to increase your chances of success</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="#" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: bold;">
                    View All Opportunities
                </a>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; margin-top: 30px;">
                <p style="margin: 0; color: #666; font-size: 14px;">
                    This weekly summary was generated by Nexora AI Agent on {datetime.now().strftime("%Y-%m-%d %H:%M")}
                </p>
                <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">
                    To update your preferences, visit your Nexora dashboard.
                </p>
            </div>
        </body>
        </html>
        """
        return html_content
    
    def send_weekly_summary(self, user_id: str) -> bool:
        """
        Send weekly summary email to a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            logger.info(f"Sending weekly summary to user {user_id}")
            
            # Get weekly summary data
            summary_data = self.personalization_service.get_weekly_summary_data(user_id)
            
            if "error" in summary_data:
                logger.error(f"Error getting weekly summary data for user {user_id}: {summary_data['error']}")
                return False
            
            user_email = summary_data.get('user_email')
            if not user_email:
                logger.warning(f"No email found for user {user_id}")
                return False
            
            # Check if user wants email notifications
            preferences = self.user_db.get_user_preferences(user_id)
            if preferences and not preferences.get('email_notifications', True):
                logger.info(f"Email notifications disabled for user {user_id}")
                return True
            
            # Create email content
            subject = f"📊 Your Weekly Opportunity Summary - {datetime.now().strftime('%B %d, %Y')}"
            html_content = self.create_weekly_summary_html(summary_data)
            
            # Send email
            success = self.email_service.send_opportunities_email([], user_email)
            
            if success:
                logger.info(f"Weekly summary sent successfully to {user_email}")
            else:
                logger.error(f"Failed to send weekly summary to {user_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending weekly summary to user {user_id}: {e}")
            return False
    
    def send_weekly_summaries_to_all_users(self) -> Dict[str, Any]:
        """
        Send weekly summary emails to all active users.
        
        Returns:
            Dictionary with summary results
        """
        try:
            logger.info("Starting weekly summary email batch")
            
            # Get all active users
            users = self.user_db.get_all_users()
            active_users = [user for user in users if user.get('is_active', True)]
            
            if not active_users:
                logger.info("No active users found for weekly summaries")
                return {
                    "total_users": 0,
                    "emails_sent": 0,
                    "emails_failed": 0
                }
            
            emails_sent = 0
            emails_failed = 0
            
            for user in active_users:
                user_id = user['id']
                try:
                    success = self.send_weekly_summary(user_id)
                    if success:
                        emails_sent += 1
                    else:
                        emails_failed += 1
                except Exception as e:
                    logger.error(f"Error sending weekly summary to user {user_id}: {e}")
                    emails_failed += 1
            
            result = {
                "total_users": len(active_users),
                "emails_sent": emails_sent,
                "emails_failed": emails_failed,
                "success_rate": emails_sent / len(active_users) if active_users else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Weekly summary batch completed: {emails_sent}/{len(active_users)} emails sent")
            return result
            
        except Exception as e:
            logger.error(f"Error in weekly summary batch: {e}")
            return {"error": str(e)}
    
    def get_weekly_summary_trigger(self) -> CronTrigger:
        """
        Get the cron trigger for weekly summaries.
        
        Returns:
            CronTrigger for weekly execution (Sundays at 9 AM)
        """
        return CronTrigger(day_of_week=6, hour=9, minute=0)  # Sunday at 9 AM
