#!/usr/bin/env python3
"""
Vortex Firewall Deployment Script
For non-technical users - simple guided setup
"""

import os
import sys
import yaml
import getpass
from pathlib import Path

class VortexDeployer:
    """Guided deployment system for non-technical users"""
    
    def __init__(self):
        self.current_dir = Path(__file__).parent.parent.parent
        self.config_dir = self.current_dir / 'config'
        
    def run_guided_setup(self):
        """Run interactive setup guide"""
        print("🚀 Vortex Meta Ads Firewall - Guided Setup")
        print("=" * 50)
        
        # Check prerequisites
        self.check_prerequisites()
        
        # Setup configuration
        self.setup_configuration()
        
        # Test connection
        self.test_connection()
        
        # Finalize setup
        self.finalize_setup()
        
    def check_prerequisites(self):
        """Check system prerequisites"""
        print("\n📋 Checking prerequisites...")
        
        checks = [
            ("Python 3.8+", self.check_python_version()),
            ("Config directory", self.check_config_dir()),
            ("Required files", self.check_required_files())
        ]
        
        all_ok = True
        for check_name, status in checks:
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {check_name}")
            if not status:
                all_ok = False
                
        if not all_ok:
            print("\n❌ Please fix the issues above before continuing.")
            sys.exit(1)
            
    def check_python_version(self):
        """Check Python version"""
        return sys.version_info >= (3, 8)
    
    def check_config_dir(self):
        """Check config directory exists"""
        return self.config_dir.exists()
    
    def check_required_files(self):
        """Check required files exist"""
        required_files = [
            self.config_dir / 'config.yaml',
            self.config_dir / 'client_config.example.yaml'
        ]
        return all(f.exists() for f in required_files)
    
    def setup_configuration(self):
        """Interactive configuration setup"""
        print("\n⚙️  Configuration Setup")
        
        # Create client config from example
        example_config = self.config_dir / 'client_config.example.yaml'
        client_config = self.config_dir / 'client_config.yaml'
        
        if client_config.exists():
            overwrite = input("Client config exists. Overwrite? (y/n): ")
            if overwrite.lower() != 'y':
                return
                
        print("\nPlease enter your Meta Ads configuration:")
        
        config_data = {
            'client': {
                'name': input("Client Business Name: "),
                'industry': input("Industry (ecommerce/lead_generation/brand_awareness): ")
            },
            'meta_api': {
                'access_token': getpass.getpass("Meta Access Token: "),
                'ad_account_id': input("Ad Account ID (act_XXXXXXXX): "),
                'business_id': input("Business ID: "),
                'app_secret': getpass.getpass("App Secret: ")
            }
        }
        
        # Save configuration
        with open(client_config, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
            
        print("✅ Configuration saved!")
    
    def test_connection(self):
        """Test Meta API connection"""
        print("\n🔌 Testing Meta API Connection...")
        
        # Import and test API
        try:
            from ..api.meta_api import MetaAPI
            import yaml
            
            with open(self.config_dir / 'client_config.yaml', 'r') as f:
                config = yaml.safe_load(f)
                
            api = MetaAPI(
                config['meta_api']['access_token'],
                config['meta_api']['ad_account_id']
            )
            
            if api.test_connection():
                print("✅ Meta API connection successful!")
            else:
                print("❌ Meta API connection failed. Please check your credentials.")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            sys.exit(1)
    
    def finalize_setup(self):
        """Finalize setup and provide next steps"""
        print("\n🎉 Setup Complete!")
        print("\nNext Steps:")
        print("1. Start the firewall: python src/main.py")
        print("2. Monitor logs: tail -f logs/firewall.log")
        print("3. Check alerts in the web interface")
        print("\nFor support: tech@vortexconsultants.com")

if __name__ == "__main__":
    deployer = VortexDeployer()
    deployer.run_guided_setup()