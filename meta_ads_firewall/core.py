import requests
import logging
import sqlite3
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_DB_DIR = Path('/var/lib/meta-ads-firewall')
DEFAULT_DB_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_DB = DEFAULT_DB_DIR / 'firewall.db'

class VortexFirewall:
    """Core firewall class for Meta Ads protection
    Minimal, cleaned implementation.
    """
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger('VortexFirewall')
        self.db_path = Path(config.get('database_path', str(DEFAULT_DB)))
        os.makedirs(self.db_path.parent, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.create_tables()
        self.suspicious_activities = []
        self.blocked_ips = set()

    def create_tables(self):
        cur = self.conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS campaign_spend (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT,
                spend REAL,
                date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,
                message TEXT,
                resource_id TEXT,
                severity TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cur.execute('''
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
        base_url = 'https://graph.facebook.com/v17.0'
        url = f'{base_url}/{endpoint}'
        default_params = {'access_token': self.config.get('meta_api', {}).get('access_token')}
        if params:
            default_params.update(params)
        try:
            self.logger.debug('API call to %s', url)
            resp = requests.get(url, params=default_params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            self.logger.exception('API call failed: %s', e)
            return None

    def get_active_campaigns(self) -> List[Dict]:
        account = self.config.get('meta_api', {}).get('ad_account_id', '')
        endpoint = f"{account}/campaigns"
        params = {'fields': 'id,name,status,daily_budget,lifetime_budget,objective'}
        result = self.make_meta_api_call(endpoint, params)
        return result.get('data', []) if result else []

    def get_campaign_insights(self, campaign_id: str, fields: List[str] = None) -> Optional[Dict]:
        if fields is None:
            fields = ['spend', 'impressions', 'clicks']
        endpoint = f"{campaign_id}/insights"
        since = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        until = datetime.now().strftime('%Y-%m-%d')
        params = {'fields': ','.join(fields), 'time_range': f'{{"since":"{since}","until":"{until}"}}'}
        result = self.make_meta_api_call(endpoint, params)
        return result.get('data', [{}])[0] if result and result.get('data') else None

    def update_normal_patterns(self):
        campaigns = self.get_active_campaigns()
        for c in campaigns:
            insights = self.get_campaign_insights(c.get('id'))
            if insights and 'spend' in insights:
                try:
                    val = float(insights['spend'])
                except Exception:
                    continue
                self._update_campaign_pattern(c.get('id'), 'daily_spend', val)

    def _update_campaign_pattern(self, campaign_id: str, metric: str, value: float):
        cur = self.conn.cursor()
        cur.execute('''
            INSERT OR REPLACE INTO normal_patterns (metric_type, resource_id, value)
            VALUES (?, ?, ?)
        ''', (metric, campaign_id, value))
        self.conn.commit()

    def record_alert(self, alert_type: str, message: str, resource_id: str, severity: str = 'MEDIUM'):
        cur = self.conn.cursor()
        cur.execute('''
            INSERT INTO security_alerts (alert_type, message, resource_id, severity)
            VALUES (?, ?, ?, ?)
        ''', (alert_type, message, resource_id, severity))
        self.conn.commit()
        self.logger.warning('Recorded alert %s: %s', alert_type, message)
