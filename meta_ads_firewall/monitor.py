import logging
from .core import VortexFirewall

class SecurityMonitor:
    def __init__(self, firewall: VortexFirewall, config: dict):
        self.logger = logging.getLogger('SecurityMonitor')
        self.firewall = firewall
        self.config = config

    def run_security_scan(self):
        self.logger.info('Running security scan')
        try:
            self.firewall.update_normal_patterns()
            self.logger.info('Security scan finished')
        except Exception as e:
            self.logger.exception('Security scan failed: %s', e)
