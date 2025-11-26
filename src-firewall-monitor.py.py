import logging
from datetime import datetime, timedelta
from typing import Dict, List
from .core import VortexFirewall

class SecurityMonitor:
    """Real-time security monitoring engine"""
    
    def __init__(self, firewall: VortexFirewall):
        self.firewall = firewall
        self.logger = logging.getLogger('SecurityMonitor')
        self.alert_thresholds = self.firewall.config['security']['thresholds']
        
    def run_security_scan(self):
        """Execute comprehensive security scan"""
        self.logger.info("Starting security scan...")
        
        campaigns = self.firewall.get_active_campaigns()
        
        for campaign in campaigns:
            self.check_spending_anomalies(campaign)
            self.check_traffic_quality(campaign)
            self.check_budget_compliance(campaign)
            
        self.firewall.update_normal_patterns()
        self.logger.info("Security scan completed")
    
    def check_spending_anomalies(self, campaign: Dict):
        """Detect unusual spending patterns"""
        campaign_id = campaign['id']
        insights = self.firewall.get_campaign_insights(campaign_id)
        
        if not insights or 'spend' not in insights:
            return
            
        current_spend = float(insights['spend'])
        historical_avg = self.get_historical_average(campaign_id, 'daily_spend')
        
        if historical_avg and historical_avg > 0:
            spend_ratio = current_spend / historical_avg
            
            if spend_ratio > self.alert_thresholds['spend_spike']:
                self.firewall.record_alert(
                    "SPENDING_SPIKE",
                    f"Campaign spending {current_spend} vs average {historical_avg} (ratio: {spend_ratio:.2f})",
                    campaign_id,
                    "HIGH" if spend_ratio > 3.0 else "MEDIUM"
                )
                
                # Auto-pause if critical
                if spend_ratio > 3.0 and self.firewall.config['security']['auto_actions']['pause_campaign_critical']:
                    self.firewall.pause_campaign(campaign_id, f"Critical spending spike: {spend_ratio:.2f}x normal")
    
    def check_traffic_quality(self, campaign: Dict):
        """Analyze traffic patterns for suspicious activity"""
        campaign_id = campaign['id']
        insights = self.firewall.get_campaign_insights(campaign_id, ['ctr', 'clicks', 'impressions'])
        
        if not insights:
            return
            
        # Check CTR anomalies
        if 'ctr' in insights:
            current_ctr = float(insights['ctr'])
            historical_ctr = self.get_historical_average(campaign_id, 'ctr')
            
            if historical_ctr and historical_ctr > 0:
                ctr_ratio = current_ctr / historical_ctr
                
                if ctr_ratio < self.alert_thresholds['ctr_drop']:
                    self.firewall.record_alert(
                        "CTR_ANOMALY",
                        f"CTR dropped to {current_ctr} from average {historical_ctr}",
                        campaign_id,
                        "MEDIUM"
                    )
        
        # Check click velocity
        if 'clicks' in insights:
            clicks = int(insights['clicks'])
            if clicks > self.alert_thresholds['suspicious_clicks']:
                self.firewall.record_alert(
                    "HIGH_CLICK_VOLUME",
                    f"Suspicious click volume: {clicks} in last 24h",
                    campaign_id,
                    "MEDIUM"
                )
    
    def check_budget_compliance(self, campaign: Dict):
        """Check if campaign is exceeding budget limits"""
        campaign_id = campaign['id']
        daily_budget = float(campaign.get('daily_budget', 0))
        
        if daily_budget > 0:
            insights = self.firewall.get_campaign_insights(campaign_id, ['spend'])
            if insights and 'spend' in insights:
                spend = float(insights['spend'])
                budget_ratio = spend / daily_budget
                
                if budget_ratio > self.alert_thresholds['budget_breach']:
                    self.firewall.record_alert(
                        "BUDGET_BREACH",
                        f"Campaign spent {spend} vs daily budget {daily_budget} (ratio: {budget_ratio:.2f})",
                        campaign_id,
                        "HIGH"
                    )
    
    def get_historical_average(self, campaign_id: str, metric: str) -> float:
        """Get historical average for a metric"""
        cursor = self.firewall.conn.cursor()
        cursor.execute('''
            SELECT AVG(value) FROM normal_patterns 
            WHERE metric_type = ? AND resource_id = ?
        ''', (metric, campaign_id))
        
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0.0