import smtplib
import logging
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict

class AlertSystem:
    """Multi-channel alert notification system"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger('AlertSystem')
        
    def send_alert(self, alert_data: Dict):
        """Send alert through configured channels"""
        alert_type = alert_data.get('type')
        message = alert_data.get('message')
        severity = alert_data.get('severity', 'MEDIUM')
        resource_id = alert_data.get('resource_id')
        
        alert_message = self.format_alert_message(alert_type, message, severity, resource_id)
        
        # Send via enabled channels
        if self.config['alerts']['email']['enabled']:
            self.send_email_alert(alert_message, severity)
            
        if self.config['alerts']['slack']['enabled']:
            self.send_slack_alert(alert_message, severity)
            
        if self.config['alerts']['sms']['enabled'] and severity in ['HIGH', 'CRITICAL']:
            self.send_sms_alert(alert_message)
    
    def format_alert_message(self, alert_type: str, message: str, severity: str, resource_id: str) -> str:
        """Format alert message for different channels"""
        return f"""
🚨 VORTEX FIREWALL ALERT 🚨

Type: {alert_type}
Severity: {severity}
Resource: {resource_id}
Message: {message}

Time: {self.get_current_timestamp()}

Please review immediately if severity is HIGH or CRITICAL.
"""
    
    def send_email_alert(self, message: str, severity: str):
        """Send email alert"""
        try:
            email_config = self.config['alerts']['email']
            contacts = self.config['alert_contacts']
            
            msg = MimeMultipart()
            msg['From'] = "vortex-firewall@vortexconsultants.com"
            msg['To'] = contacts['primary']
            msg['Subject'] = f"Vortex Firewall Alert - {severity}"
            
            if severity in ['HIGH', 'CRITICAL']:
                msg['To'] = f"{contacts['primary']}, {contacts['emergency']}"
            
            msg.attach(MimeText(message, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            # Note: In production, use environment variables for credentials
            # server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email alert sent for {severity} issue")
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    def send_slack_alert(self, message: str, severity: str):
        """Send Slack alert"""
        try:
            # Implementation for Slack webhook
            pass
        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {e}")
    
    def send_sms_alert(self, message: str):
        """Send SMS alert for critical issues"""
        try:
            # Implementation for Twilio SMS
            pass
        except Exception as e:
            self.logger.error(f"Failed to send SMS alert: {e}")
    
    def get_current_timestamp(self):
        """Get formatted current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")