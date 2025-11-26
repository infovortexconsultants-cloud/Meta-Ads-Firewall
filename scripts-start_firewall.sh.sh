#!/bin/bash

# Start Vortex Firewall
echo "🚀 Starting Vortex Meta Ads Firewall..."

# Activate virtual environment
source vortex-env/bin/activate

# Check if configuration exists
if [ ! -f config/client_config.yaml ]; then
    echo "❌ Configuration file not found. Please run setup first."
    echo "Run: python src/deployment/deploy.py"
    exit 1
fi

# Start the firewall
python src/main.py

echo "✅ Firewall started. Check logs/firewall.log for details."