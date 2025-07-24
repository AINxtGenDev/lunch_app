"""
Task scheduler for automated scraping
"""

from apscheduler.schedulers.background import BackgroundScheduler
import logging

logger = logging.getLogger(__name__)

def setup_scheduler(app, socketio):
    """Set up the APScheduler for automated scraping"""
    scheduler = BackgroundScheduler()

    # TODO: Add scheduled jobs

    scheduler.start()
    logger.info("Scheduler started")

    return scheduler
