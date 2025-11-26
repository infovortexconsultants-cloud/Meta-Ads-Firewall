#!/bin/bash

# Vortex Firewall Installation Script
echo "🛡️  Installing Vortex Meta Ads Firewall..."

# Check Python version
python3 -c "import sys; assert sys.version_info >= (3, 8), 'Python 3.8+ required'; print('✅ Python version OK')"

# Create virtual environment
echo "📦 Setting up virtual environment..."
python3 -m venv vortex-env
source vortex-env/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data config

# Setup configuration
echo "⚙️  Setting up configuration..."
if [ ! -f config/client_config.yaml ]; then
    cp config/client_config.example.yaml config/client_config.yaml
    echo "📝 Please edit config/client_config.yaml with your Meta API credentials"
fi

# Set permissions
chmod +x scripts/*.sh

echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit config/client_config.yaml with your Meta API credentials"
echo "2. Run: source vortex-env/bin/activate"
echo "3. Run: python src/deployment/deploy.py"
echo "4. Start monitoring: python src/main.py"