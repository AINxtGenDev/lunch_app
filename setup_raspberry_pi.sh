#!/bin/bash
# Setup script for Cyclist OCR scraper on Raspberry Pi

echo "Setting up Cyclist OCR scraper for Raspberry Pi..."

# Update system packages
echo "Updating system packages..."
sudo apt-get update

# Install Tesseract OCR with German language support
echo "Installing Tesseract OCR with German language support..."
sudo apt-get install -y tesseract-ocr tesseract-ocr-deu

# Install Chromium browser and driver for ARM architecture
echo "Installing Chromium browser and driver for Raspberry Pi..."
sudo apt-get install -y chromium-browser chromium-chromedriver

# Create symlink for chromedriver if needed
if [ ! -f /usr/bin/chromedriver ]; then
    echo "Creating chromedriver symlink..."
    sudo ln -s /usr/lib/chromium-browser/chromedriver /usr/bin/chromedriver
fi

# Install Python packages
echo "Installing Python packages..."
source ~/miniconda3/bin/activate lunch-menu-app  # Adjust path as needed
pip install pytesseract pillow

# Test Tesseract installation
echo "Testing Tesseract installation..."
tesseract --version

# Test chromedriver
echo "Testing chromedriver..."
chromedriver --version

echo "Setup complete!"
echo ""
echo "Important notes for Raspberry Pi:"
echo "1. The scraper will use system chromedriver (/usr/bin/chromedriver) instead of downloading"
echo "2. If Selenium fails, the scraper will fall back to direct image download"
echo "3. OCR processing may be slower on Raspberry Pi - be patient"
echo ""
echo "To test the scraper, run:"
echo "  cd /home/stecher/lunch_app"
echo "  python test_cyclist_scraper.py"