import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
import sqlite3
import os

class VortexFirewall:
    """Core firewall class for Meta Ads protection"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.setup_logging()
        self.setup_database()
        self.suspicious_activities = []
        self.blocked_ips = set()
        
    def setup_logging(self):
        """Configure logging"""
        log_config = self.config.get('logging', {})
        logging.basicConfig(
            level=log_config.get('level', 'INFO'),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config.get('file_path', 'logs/firewall.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('VortexFirewall')
        
    def setup_database(self):
        """Initialize SQLite database for historical data"""
        os.makedirs('data', exist_ok=True)
        self.conn = sqlite3.connect('data/firewall.db', check_same_thread=False)
        self.create_tables()
        
    def create_tables(self):
        """Create necessary database tables"""
        cursor = self.conn.cursor()
        
        # Campaign spending history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_spend (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT,
                spend REAL,
                date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Security alerts log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,
                message TEXT,
                resource_id TEXT,
                severity TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Normal patterns baseline
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS normal_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT,
                resource_id TEXT,
                value REAL,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        
    def make_meta_api_call(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Secure API call to Meta Graph API"""
        base_url = "https://graph.facebook.com/v17.0"
        url = f"{base_url}/{endpoint}"
        
        default_params = {
            'access_token': self.config['meta_api']['access_token'],
            'limit': 1000
        }
        
        if params:
            default_params.update(params)
            
        try:
            self.logger.info(f"Making API call to: {endpoint}")
            response = requests.get(url, params=default_params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API call failed to {endpoint}: {e}")
            return None
            
    def get_active_campaigns(self) -> List[Dict]:
        """Fetch all active campaigns"""
        endpoint = f"{self.config['meta_api']['ad_account_id']}/campaigns"
        params = {
            'fields': 'id,name,status,daily_budget,lifetime_budget,objective',
            'effective_status': ['ACTIVE', 'PAUSED']
        }
        
        result = self.make_meta_api_call(endpoint, params)
        return result.get('data', []) if result else []
    
    def get_campaign_insights(self, campaign_id: str, fields: List[str] = None) -> Optional[Dict]:
        """Get campaign performance insights"""
        if fields is None:
            fields = ['spend', 'impressions', 'clicks', 'ctr', 'actions']
            
        endpoint = f"{campaign_id}/insights"
        params = {
            'fields': ','.join(fields),
            'time_range': '{"since":"' + (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d') + '","until":"' + datetime.now().strftime('%Y-%m-%d') + '"}'
        }
        
        result = self.make_meta_api_call(endpoint, params)
        return result.get('data', [{}])[0] if result and result.get('data') else None
    
    def pause_campaign(self, campaign_id: str, reason: str):
        """Pause a campaign for security reasons"""
        endpoint = f"{campaign_id}"
        params = {
            'access_token': self.config['meta_api']['access_token'],
            'status': 'PAUSED'
        }
        
        try:
            response = requests.post(url=f"https://graph.facebook.com/v17.0/{endpoint}", data=params)
            if response.status_code == 200:
                self.logger.warning(f"Campaign {campaign_id} paused: {reason}")
                self.record_alert("CAMPAIGN_PAUSED", f"Campaign paused: {reason}", campaign_id, "HIGH")
            else:
                self.logger.error(f"Failed to pause campaign {campaign_id}: {response.text}")
        except Exception as e:
            self.logger.error(f"Error pausing campaign {campaign_id}: {e}")
    
    def record_alert(self, alert_type: str, message: str, resource_id: str, severity: str = "MEDIUM"):
        """Record security alert in database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO security_alerts (alert_type, message, resource_id, severity)
            VALUES (?, ?, ?, ?)
        ''', (alert_type, message, resource_id, severity))
        self.conn.commit()
        
        # Trigger alert notifications
        self.trigger_alert_notification(alert_type, message, resource_id, severity)
    
    def trigger_alert_notification(self, alert_type: str, message: str, resource_id: str, severity: str):
        """Trigger external alert notifications"""
        # This will be implemented in alerts.py
        pass
    
    def update_normal_patterns(self):
        """Update baseline normal patterns from historical data"""
        campaigns = self.get_active_campaigns()
        for campaign in campaigns:
            insights = self.get_campaign_insights(campaign['id'])
            if insights and 'spend' in insights:
                self._update_campaign_pattern(campaign['id'], 'daily_spend', float(insights['spend']))
    
    def _update_campaign_pattern(self, campaign_id: str, metric: str, value: float):
        """Update pattern for specific campaign metric"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLICE INTO normal_patterns (metric_type, resource_id, value)
            VALUES (?, ?, ?)
        ''', (metric, campaign_id, value))
        self.conn.commit()