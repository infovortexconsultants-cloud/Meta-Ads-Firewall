#!/usr/bin/env python3
"""
Vortex Meta Ads Firewall - Main Entry Point
"""

import time
import logging
import yaml
from pathlib import Path

from firewall.core import VortexFirewall
from firewall.monitor import SecurityMonitor
from firewall.alerts import AlertSystem

def load_config():
    """Load configuration from YAML files"""
    config_path = Path('config/config.yaml')
    client_config_path = Path('config/client_config.yaml')
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    with open(client_config_path, 'r') as f:
        client_config = yaml.safe_load(f)
    
    # Merge configurations
    config.update(client_config)
    return config

def main():
    """Main application loop"""
    print("🛡️  Starting Vortex Meta Ads Firewall...")
    
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return
    
    # Initialize components
    firewall = VortexFirewall(config)
    monitor = SecurityMonitor(firewall)
    alert_system = AlertSystem(config)
    
    # Test Meta API connection
    from api.meta_api import MetaAPI
    api = MetaAPI(
        config['meta_api']['access_token'],
        config['meta_api']['ad_account_id']
    )
    
    if not api.test_connection():
        print("❌ Meta API connection failed. Please check your credentials.")
        return
    
    print("✅ Vortex Firewall initialized successfully!")
    print(f"📊 Monitoring interval: {config['firewall']['monitoring_interval']} seconds")
    print("🔄 Starting continuous monitoring...")
    
    # Main monitoring loop
    monitoring_interval = config['firewall']['monitoring_interval']
    
    try:
        while True:
            monitor.run_security_scan()
            print(f"✅ Security scan completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(monitoring_interval)
            
    except KeyboardInterrupt:
        print("\n🛑 Vortex Firewall stopped by user")
    except Exception as e:
        print(f"❌ Vortex Firewall crashed: {e}")
        logging.error(f"Firewall crash: {e}")

if __name__ == "__main__":
    main()