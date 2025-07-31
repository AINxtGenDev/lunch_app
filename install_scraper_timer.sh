#!/bin/bash

# Installation script for lunch scraper systemd timer
# Run with: sudo bash install_scraper_timer.sh

set -e

echo "Installing Lunch Menu Scraper Timer..."

# Copy service files to systemd directory
cp lunch-scraper.service /etc/systemd/system/
cp lunch-scraper.timer /etc/systemd/system/

# Reload systemd to recognize new services
systemctl daemon-reload

# Enable and start the timer
systemctl enable lunch-scraper.timer
systemctl start lunch-scraper.timer

# Check status
echo ""
echo "Installation complete! Checking status..."
echo ""
systemctl status lunch-scraper.timer --no-pager

echo ""
echo "Timer schedule:"
systemctl list-timers lunch-scraper.timer --no-pager

echo ""
echo "Useful commands:"
echo "  - Check timer status: systemctl status lunch-scraper.timer"
echo "  - Check last scrape: systemctl status lunch-scraper.service"
echo "  - View logs: journalctl -u lunch-scraper.service"
echo "  - Run manually: systemctl start lunch-scraper.service"
echo "  - Disable scraper: systemctl disable lunch-scraper.timer"