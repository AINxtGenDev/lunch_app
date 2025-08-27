# app/services/scraper_monitor.py
"""
Production monitoring service for scraper health and performance tracking.
Provides alerting, metrics, and health status monitoring for all scrapers.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logger = logging.getLogger("scraper_monitor")


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ScraperMetrics:
    """Dataclass for scraper performance metrics."""
    scraper_name: str
    scrape_attempts: int = 0
    successful_scrapes: int = 0
    failed_scrapes: int = 0
    fallback_usage: int = 0
    avg_execution_time: float = 0.0
    last_successful_scrape: Optional[datetime] = None
    last_error: Optional[str] = None
    health_score: float = 100.0
    content_freshness: float = 0.0
    

class ScraperMonitor:
    """Production monitoring service for scrapers."""
    
    def __init__(self, metrics_file: str = "scraper_metrics.json"):
        self.metrics_file = metrics_file
        self.metrics: Dict[str, ScraperMetrics] = {}
        self.load_metrics()
        
        # Alert thresholds
        self.thresholds = {
            'health_score_warning': 80.0,
            'health_score_critical': 60.0,
            'max_hours_without_success': 24,
            'max_consecutive_failures': 5,
            'max_execution_time': 300.0  # 5 minutes
        }
    
    def load_metrics(self):
        """Load metrics from persistent storage."""
        try:
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                
                for scraper_name, metrics_data in data.items():
                    # Convert datetime strings back to datetime objects
                    if metrics_data.get('last_successful_scrape'):
                        metrics_data['last_successful_scrape'] = datetime.fromisoformat(
                            metrics_data['last_successful_scrape']
                        )
                    
                    self.metrics[scraper_name] = ScraperMetrics(**metrics_data)
                
                logger.info(f"Loaded metrics for {len(self.metrics)} scrapers")
                
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
            self.metrics = {}
    
    def save_metrics(self):
        """Save metrics to persistent storage."""
        try:
            # Convert to JSON-serializable format
            data = {}
            for scraper_name, metrics in self.metrics.items():
                metrics_dict = asdict(metrics)
                
                # Convert datetime to string
                if metrics_dict.get('last_successful_scrape'):
                    metrics_dict['last_successful_scrape'] = metrics_dict['last_successful_scrape'].isoformat()
                
                data[scraper_name] = metrics_dict
            
            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def record_scrape_start(self, scraper_name: str):
        """Record the start of a scraping operation."""
        if scraper_name not in self.metrics:
            self.metrics[scraper_name] = ScraperMetrics(scraper_name=scraper_name)
        
        self.metrics[scraper_name].scrape_attempts += 1
        logger.info(f"📊 Started scrape for {scraper_name}")
    
    def record_scrape_success(self, scraper_name: str, execution_time: float, items_found: int, using_fallback: bool = False):
        """Record a successful scraping operation."""
        if scraper_name not in self.metrics:
            self.metrics[scraper_name] = ScraperMetrics(scraper_name=scraper_name)
        
        metrics = self.metrics[scraper_name]
        metrics.successful_scrapes += 1
        metrics.last_successful_scrape = datetime.now()
        
        # Update average execution time
        total_time = metrics.avg_execution_time * (metrics.successful_scrapes - 1) + execution_time
        metrics.avg_execution_time = total_time / metrics.successful_scrapes
        
        if using_fallback:
            metrics.fallback_usage += 1
        
        # Update health score
        metrics.health_score = self.calculate_health_score(metrics)
        
        logger.info(f"✅ Scrape successful for {scraper_name}: {items_found} items in {execution_time:.1f}s")
        self.save_metrics()
    
    def record_scrape_failure(self, scraper_name: str, error: str, execution_time: float = 0):
        """Record a failed scraping operation."""
        if scraper_name not in self.metrics:
            self.metrics[scraper_name] = ScraperMetrics(scraper_name=scraper_name)
        
        metrics = self.metrics[scraper_name]
        metrics.failed_scrapes += 1
        metrics.last_error = error
        
        # Update health score
        metrics.health_score = self.calculate_health_score(metrics)
        
        # Check if we need to send alerts
        self.check_and_send_alerts(scraper_name, metrics)
        
        logger.error(f"❌ Scrape failed for {scraper_name}: {error}")
        self.save_metrics()
    
    def calculate_health_score(self, metrics: ScraperMetrics) -> float:
        """Calculate health score based on various factors."""
        if metrics.scrape_attempts == 0:
            return 100.0
        
        # Base score from success rate
        success_rate = metrics.successful_scrapes / metrics.scrape_attempts
        base_score = success_rate * 100
        
        # Penalties
        penalties = 0
        
        # Penalty for excessive fallback usage
        if metrics.successful_scrapes > 0:
            fallback_rate = metrics.fallback_usage / metrics.successful_scrapes
            penalties += fallback_rate * 20  # Up to 20 points penalty
        
        # Penalty for no recent success
        if metrics.last_successful_scrape:
            hours_since_success = (datetime.now() - metrics.last_successful_scrape).total_seconds() / 3600
            if hours_since_success > 24:
                penalties += min(hours_since_success, 48) * 2  # Up to 96 points penalty
        
        # Penalty for slow execution
        if metrics.avg_execution_time > 60:
            penalties += (metrics.avg_execution_time - 60) / 10  # 1 point per 10s over 1 minute
        
        final_score = max(0, min(100, base_score - penalties))
        return round(final_score, 1)
    
    def check_and_send_alerts(self, scraper_name: str, metrics: ScraperMetrics):
        """Check conditions and send alerts if necessary."""
        alerts = []
        
        # Critical health score
        if metrics.health_score < self.thresholds['health_score_critical']:
            alerts.append({
                'level': AlertLevel.CRITICAL,
                'message': f"Scraper {scraper_name} health critically low: {metrics.health_score}%"
            })
        elif metrics.health_score < self.thresholds['health_score_warning']:
            alerts.append({
                'level': AlertLevel.WARNING,
                'message': f"Scraper {scraper_name} health below threshold: {metrics.health_score}%"
            })
        
        # No recent success
        if metrics.last_successful_scrape:
            hours_since_success = (datetime.now() - metrics.last_successful_scrape).total_seconds() / 3600
            if hours_since_success > self.thresholds['max_hours_without_success']:
                alerts.append({
                    'level': AlertLevel.CRITICAL,
                    'message': f"Scraper {scraper_name} has not succeeded in {hours_since_success:.1f} hours"
                })
        
        # Consecutive failures
        recent_failure_rate = self.get_recent_failure_rate(scraper_name)
        if recent_failure_rate >= self.thresholds['max_consecutive_failures']:
            alerts.append({
                'level': AlertLevel.ERROR,
                'message': f"Scraper {scraper_name} has {recent_failure_rate} consecutive failures"
            })
        
        # Send alerts
        for alert in alerts:
            self.send_alert(alert['level'], alert['message'])
    
    def get_recent_failure_rate(self, scraper_name: str) -> int:
        """Get number of recent consecutive failures (simplified implementation)."""
        # In a real implementation, this would track individual scrape attempts
        # For now, we'll use a simple heuristic
        metrics = self.metrics.get(scraper_name)
        if not metrics:
            return 0
        
        if metrics.scrape_attempts == 0:
            return 0
        
        recent_success_rate = metrics.successful_scrapes / metrics.scrape_attempts
        
        # If success rate is very low, assume recent failures
        if recent_success_rate < 0.5:
            return min(5, metrics.failed_scrapes)
        
        return 0
    
    def send_alert(self, level: AlertLevel, message: str):
        """Send alert (can be extended to email, Slack, etc.)."""
        # For now, just log the alert
        if level == AlertLevel.CRITICAL:
            logger.critical(f"🚨 CRITICAL ALERT: {message}")
        elif level == AlertLevel.ERROR:
            logger.error(f"🔥 ERROR ALERT: {message}")
        elif level == AlertLevel.WARNING:
            logger.warning(f"⚠️ WARNING ALERT: {message}")
        else:
            logger.info(f"ℹ️ INFO ALERT: {message}")
        
        # TODO: Add email/Slack/webhook notifications here
        self.log_alert_to_file(level, message)
    
    def log_alert_to_file(self, level: AlertLevel, message: str):
        """Log alert to dedicated alert file."""
        try:
            alert_file = "scraper_alerts.log"
            timestamp = datetime.now().isoformat()
            
            with open(alert_file, 'a') as f:
                f.write(f"{timestamp} [{level.value.upper()}] {message}\n")
                
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")
    
    def get_scraper_status(self, scraper_name: str) -> Optional[Dict]:
        """Get detailed status for a specific scraper."""
        if scraper_name not in self.metrics:
            return None
        
        metrics = self.metrics[scraper_name]
        
        return {
            'scraper_name': scraper_name,
            'health_score': metrics.health_score,
            'scrape_attempts': metrics.scrape_attempts,
            'success_rate': (metrics.successful_scrapes / metrics.scrape_attempts * 100) if metrics.scrape_attempts > 0 else 0,
            'fallback_usage_rate': (metrics.fallback_usage / metrics.successful_scrapes * 100) if metrics.successful_scrapes > 0 else 0,
            'avg_execution_time': metrics.avg_execution_time,
            'last_successful_scrape': metrics.last_successful_scrape.isoformat() if metrics.last_successful_scrape else None,
            'last_error': metrics.last_error,
            'content_freshness': metrics.content_freshness
        }
    
    def get_all_scrapers_status(self) -> Dict[str, Dict]:
        """Get status for all monitored scrapers."""
        status = {}
        for scraper_name in self.metrics:
            status[scraper_name] = self.get_scraper_status(scraper_name)
        
        return status
    
    def generate_health_report(self) -> str:
        """Generate a comprehensive health report."""
        report_lines = [
            "🏥 SCRAPER HEALTH REPORT",
            "=" * 50,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        if not self.metrics:
            report_lines.append("No scrapers monitored yet.")
            return "\n".join(report_lines)
        
        # Overall summary
        total_scrapers = len(self.metrics)
        healthy_scrapers = sum(1 for m in self.metrics.values() if m.health_score >= 80)
        critical_scrapers = sum(1 for m in self.metrics.values() if m.health_score < 60)
        
        report_lines.extend([
            f"📊 OVERVIEW:",
            f"   Total Scrapers: {total_scrapers}",
            f"   Healthy (≥80%): {healthy_scrapers}",
            f"   Critical (<60%): {critical_scrapers}",
            ""
        ])
        
        # Individual scraper status
        report_lines.append("🔍 INDIVIDUAL SCRAPER STATUS:")
        for scraper_name, metrics in sorted(self.metrics.items()):
            status_icon = "✅" if metrics.health_score >= 80 else "⚠️" if metrics.health_score >= 60 else "🚨"
            last_success = metrics.last_successful_scrape.strftime('%Y-%m-%d %H:%M') if metrics.last_successful_scrape else "Never"
            
            report_lines.extend([
                f"   {status_icon} {scraper_name}:",
                f"      Health Score: {metrics.health_score}%",
                f"      Success Rate: {(metrics.successful_scrapes/metrics.scrape_attempts*100):.1f}%" if metrics.scrape_attempts > 0 else "      Success Rate: N/A",
                f"      Last Success: {last_success}",
                f"      Avg Time: {metrics.avg_execution_time:.1f}s",
                ""
            ])
        
        return "\n".join(report_lines)
    
    def reset_metrics(self, scraper_name: str):
        """Reset metrics for a specific scraper."""
        if scraper_name in self.metrics:
            self.metrics[scraper_name] = ScraperMetrics(scraper_name=scraper_name)
            self.save_metrics()
            logger.info(f"🔄 Reset metrics for {scraper_name}")


# Global monitor instance
scraper_monitor = ScraperMonitor()