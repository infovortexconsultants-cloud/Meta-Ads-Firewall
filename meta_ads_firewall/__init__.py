"""
Vortex Meta Ads Firewall - package entry and main
"""
__all__ = ['VortexFirewall','SecurityMonitor','AlertSystem','MetaAPI','main']

import argparse
import logging
import signal
import sys
import time
from pathlib import Path
import yaml

from .core import VortexFirewall
from .monitor import SecurityMonitor
from .alerts import AlertSystem
from .api.meta_api import MetaAPI

BANNER = "Vortex - Meta Ads Firewall"

def load_config(path: Path):
    if not path.exists():
        raise FileNotFoundError(f'Config not found: {path}')
    with open(path, 'r') as f:
        return yaml.safe_load(f) or {}

def main(argv=None):
    parser = argparse.ArgumentParser(prog='meta-ads-firewall')
    parser.add_argument('--config', '-c', help='Configuration file path', default='/etc/meta-ads-firewall/config.yaml')
    args = parser.parse_args(argv)

    print(BANNER)

    config_path = Path(args.config)
    # Fallback to local config if system config absent
    if not config_path.exists():
        local = Path('config/config.yaml')
        if local.exists():
            config_path = local

    try:
        config = load_config(config_path)
    except Exception as e:
        print(f'ERROR: Failed to load configuration: {e}', file=sys.stderr)
        return 2

    log_level = config.get('logging', {}).get('level', 'INFO')
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO),
                        format='%(asctime)s %(name)s %(levelname)s: %(message)s',
                        handlers=[logging.StreamHandler()])
    logger = logging.getLogger('meta_ads_firewall')

    fw = VortexFirewall(config)
    monitor = SecurityMonitor(fw, config)
    alerts = AlertSystem(config)

    api_cfg = config.get('meta_api', {})
    api = MetaAPI(access_token=api_cfg.get('access_token'), ad_account_id=api_cfg.get('ad_account_id'))

    if not api.test_connection():
        logger.error('Meta API connection test failed. Check configuration.')
        return 3

    stop = {'flag': False}
    def _handle(signum, frame):
        logger.info('Received termination signal')
        stop['flag'] = True

    signal.signal(signal.SIGTERM, _handle)
    signal.signal(signal.SIGINT, _handle)

    interval = int(config.get('firewall', {}).get('monitoring_interval', 60))
    logger.info('Starting Vortex firewall (interval=%s seconds)', interval)

    try:
        while not stop['flag']:
            try:
                monitor.run_security_scan()
            except Exception as e:
                logger.exception('Monitoring loop error: %s', e)
            # responsive sleep
            for _ in range(max(1, interval)):
                if stop['flag']:
                    break
                time.sleep(1)
    except Exception as e:
        logger.exception('Fatal error in main loop: %s', e)
        return 4

    logger.info('Vortex firewall stopped')
    return 0
