import logging

class AlertSystem:
    def __init__(self, config: dict):
        self.logger = logging.getLogger('AlertSystem')
        self.config = config

    def send(self, alert_type: str, message: str, severity: str = 'MEDIUM'):
        # Placeholder: log to systemd/journal. Integrations can be added later.
        self.logger.warning('ALERT [%s] %s: %s', severity, alert_type, message)
