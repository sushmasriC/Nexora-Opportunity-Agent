"""
Scheduling system for Nexora AI Agent.
Handles hourly updates and background task processing.
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore

from .agent import NexoraAgent
from .database.user_db import UserDatabase
from .models import UserProfile, OpportunityType
from .services.personalization_service import PersonalizationService

logger = logging.getLogger(__name__)


class NexoraScheduler:
    """Scheduler for automated opportunity matching and notifications."""
    
    def __init__(self, agent: NexoraAgent, user_db: UserDatabase, personalization_service: PersonalizationService = None):
        """
        Initialize the scheduler.
        
        Args:
            agent: NexoraAgent instance
            user_db: UserDatabase instance
            personalization_service: PersonalizationService instance
        """
        self.agent = agent
        self.user_db = user_db
        self.personalization_service = personalization_service
        self.scheduler = None
        self.is_running = False
        
        # Job store and executor configuration
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(max_workers=5)
        }
        job_defaults = {
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 300  # 5 minutes
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
    
    def start(self):
        """Start the scheduler."""
        if not self.is_running:
            try:
                self.scheduler.start()
                self.is_running = True
                logger.info("Nexora scheduler started successfully")
                
                # Add default jobs
                self._add_default_jobs()
                
            except Exception as e:
                logger.error(f"Error starting scheduler: {e}")
                raise
    
    def stop(self):
        """Stop the scheduler."""
        if self.is_running:
            try:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("Nexora scheduler stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping scheduler: {e}")
    
    def _add_default_jobs(self):
        """Add default scheduled jobs."""
        try:
            # Hourly opportunity matching job
            self.scheduler.add_job(
                func=self.run_hourly_matching,
                trigger=IntervalTrigger(hours=1),
                id='hourly_matching',
                name='Hourly Opportunity Matching',
                replace_existing=True
            )
            
            # Daily cleanup job (at 2 AM UTC)
            self.scheduler.add_job(
                func=self.run_daily_cleanup,
                trigger=CronTrigger(hour=2, minute=0),
                id='daily_cleanup',
                name='Daily Cleanup Tasks',
                replace_existing=True
            )
            
            # Weekly statistics job (Sundays at 3 AM UTC)
            self.scheduler.add_job(
                func=self.run_weekly_statistics,
                trigger=CronTrigger(day_of_week=6, hour=3, minute=0),
                id='weekly_statistics',
                name='Weekly Statistics Report',
                replace_existing=True
            )
            
            logger.info("Default scheduled jobs added successfully")
            
        except Exception as e:
            logger.error(f"Error adding default jobs: {e}")
    
    def run_hourly_matching(self):
        """
        Run hourly opportunity matching for all active users.
        This is the main scheduled task.
        """
        logger.info("Starting hourly opportunity matching...")
        start_time = datetime.now()
        
        try:
            # Get all active users
            users = self.user_db.get_all_users()
            active_users = [user for user in users if user.get('is_active', True)]
            
            if not active_users:
                logger.info("No active users found for matching")
                return
            
            logger.info(f"Processing {len(active_users)} active users")
            
            # Process each user
            processed_count = 0
            success_count = 0
            
            for user in active_users:
                try:
                    user_id = user['id']
                    email = user['email']
                    
                    # Get user profile
                    profile = self.user_db.get_user_profile(user_id)
                    if not profile:
                        logger.warning(f"No profile found for user {user_id}")
                        continue
                    
                    # Set email from user data
                    profile.email = email
                    
                    # Get user preferences
                    preferences = self.user_db.get_user_preferences(user_id)
                    if not preferences:
                        logger.warning(f"No preferences found for user {user_id}")
                        continue
                    
                    # Check if user wants email notifications
                    if not preferences.get('email_notifications', True):
                        logger.info(f"Email notifications disabled for user {user_id}")
                        continue
                    
                    # Run matching workflow with personalization
                    if self.personalization_service:
                        # Use personalization service for better matching
                        opportunities = self.agent.fetch_opportunities(limit_per_source=5)
                        result = self.personalization_service.generate_personalized_recommendations(user_id, opportunities)
                        
                        if "error" not in result:
                            success_count += 1
                            logger.info(f"Successfully processed user {user_id}: {result['total_matches']} matches")
                        else:
                            logger.error(f"Failed to process user {user_id}: {result.get('error', 'Unknown error')}")
                    else:
                        # Fallback to original matching
                        result = self._run_user_matching(profile, preferences)
                        
                        if result['success']:
                            success_count += 1
                            logger.info(f"Successfully processed user {user_id}: {result['matches_found']} matches")
                        else:
                            logger.error(f"Failed to process user {user_id}: {result.get('error', 'Unknown error')}")
                    
                    processed_count += 1
                    
                    # Small delay to prevent overwhelming APIs
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing user {user_id}: {e}")
                    continue
            
            # Log summary
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Hourly matching completed: {success_count}/{processed_count} users processed successfully in {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Error in hourly matching: {e}")
    
    def _run_user_matching(self, profile: UserProfile, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run matching workflow for a single user.
        
        Args:
            profile: User profile
            preferences: User preferences
            
        Returns:
            Workflow result
        """
        try:
            # Get matching parameters from preferences
            min_score = preferences.get('min_match_score', 0.3)
            max_results = preferences.get('max_results', 15)
            limit_per_source = 10  # Reasonable limit for scheduled runs
            
            # Run the matching workflow
            result = self.agent.run_full_workflow(
                user_profile=profile,
                limit_per_source=limit_per_source,
                min_score=min_score,
                max_results=max_results
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in user matching for {profile.user_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_id": profile.user_id
            }
    
    def run_daily_cleanup(self):
        """Run daily cleanup tasks."""
        logger.info("Starting daily cleanup tasks...")
        
        try:
            # Clean up expired sessions
            deleted_sessions = self.user_db.cleanup_expired_sessions()
            logger.info(f"Cleaned up {deleted_sessions} expired sessions")
            
            # Clean up old cache entries (if using Redis)
            if hasattr(self.agent, 'cache_service'):
                # Clear old cached opportunities
                self.agent.cache_service.clear()
                logger.info("Cleared old cached data")
            
            logger.info("Daily cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"Error in daily cleanup: {e}")
    
    def run_weekly_statistics(self):
        """Run weekly statistics and reporting."""
        logger.info("Starting weekly statistics...")
        
        try:
            # Get user statistics
            users = self.user_db.get_all_users()
            active_users = [user for user in users if user.get('is_active', True)]
            
            stats = {
                "total_users": len(users),
                "active_users": len(active_users),
                "new_users_this_week": 0,  # Would need to implement date filtering
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Weekly statistics: {stats}")
            
            # In a real implementation, you might send this to an admin email
            # or store it in a statistics table
            
        except Exception as e:
            logger.error(f"Error in weekly statistics: {e}")
    
    def add_custom_job(self, func, trigger, job_id: str, name: str = None, **kwargs):
        """
        Add a custom scheduled job.
        
        Args:
            func: Function to execute
            trigger: APScheduler trigger
            job_id: Unique job ID
            name: Job name
            **kwargs: Additional job parameters
        """
        try:
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                name=name or job_id,
                replace_existing=True,
                **kwargs
            )
            logger.info(f"Custom job added: {job_id}")
            
        except Exception as e:
            logger.error(f"Error adding custom job {job_id}: {e}")
    
    def remove_job(self, job_id: str):
        """
        Remove a scheduled job.
        
        Args:
            job_id: Job ID to remove
        """
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Job removed: {job_id}")
            
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}")
    
    def get_job_status(self) -> Dict[str, Any]:
        """
        Get status of all scheduled jobs.
        
        Returns:
            Dictionary with job status information
        """
        try:
            jobs = self.scheduler.get_jobs()
            job_info = []
            
            for job in jobs:
                job_info.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                })
            
            return {
                "scheduler_running": self.is_running,
                "total_jobs": len(jobs),
                "jobs": job_info
            }
            
        except Exception as e:
            logger.error(f"Error getting job status: {e}")
            return {"error": str(e)}
    
    def run_immediate_matching(self, user_id: str) -> Dict[str, Any]:
        """
        Run immediate matching for a specific user (not scheduled).
        
        Args:
            user_id: User ID to process
            
        Returns:
            Matching result
        """
        logger.info(f"Running immediate matching for user: {user_id}")
        
        try:
            # Get user profile
            profile = self.user_db.get_user_profile(user_id)
            if not profile:
                return {
                    "success": False,
                    "error": "User profile not found"
                }
            
            # Get user data for email
            user_data = self.user_db.get_user(user_id)
            if user_data:
                profile.email = user_data['email']
            
            # Get user preferences
            preferences = self.user_db.get_user_preferences(user_id)
            if not preferences:
                preferences = {}  # Use defaults
            
            # Run matching
            result = self._run_user_matching(profile, preferences)
            
            logger.info(f"Immediate matching completed for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error in immediate matching for user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def pause_job(self, job_id: str):
        """Pause a specific job."""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Job paused: {job_id}")
        except Exception as e:
            logger.error(f"Error pausing job {job_id}: {e}")
    
    def resume_job(self, job_id: str):
        """Resume a specific job."""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Job resumed: {job_id}")
        except Exception as e:
            logger.error(f"Error resuming job {job_id}: {e}")


class SchedulerManager:
    """Manager class for the scheduling system."""
    
    def __init__(self):
        """Initialize the scheduler manager."""
        self.scheduler = None
        self.agent = None
        self.user_db = None
    
    def initialize(self, agent: NexoraAgent, user_db: UserDatabase, personalization_service: PersonalizationService = None):
        """
        Initialize the scheduler with dependencies.
        
        Args:
            agent: NexoraAgent instance
            user_db: UserDatabase instance
            personalization_service: PersonalizationService instance
        """
        self.agent = agent
        self.user_db = user_db
        self.scheduler = NexoraScheduler(agent, user_db, personalization_service)
        logger.info("Scheduler manager initialized")
    
    def start_scheduler(self):
        """Start the scheduler."""
        if self.scheduler:
            self.scheduler.start()
        else:
            logger.error("Scheduler not initialized")
    
    def stop_scheduler(self):
        """Stop the scheduler."""
        if self.scheduler:
            self.scheduler.stop()
        else:
            logger.error("Scheduler not initialized")
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status."""
        if self.scheduler:
            return self.scheduler.get_job_status()
        else:
            return {"error": "Scheduler not initialized"}
    
    def run_immediate_matching(self, user_id: str) -> Dict[str, Any]:
        """Run immediate matching for a user."""
        if self.scheduler:
            return self.scheduler.run_immediate_matching(user_id)
        else:
            return {"error": "Scheduler not initialized"}
