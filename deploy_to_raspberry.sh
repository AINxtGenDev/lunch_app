#!/bin/bash

# Raspberry Pi deployment script for Lunch App
# Run this on your Raspberry Pi after copying the files

echo "Setting up Lunch App on Raspberry Pi..."

# Create logs directory
mkdir -p /home/stecher/lunch_app/logs

# Ensure proper permissions
chmod +x /home/stecher/lunch_app/deploy_to_raspberry.sh
chmod 755 /home/stecher/lunch_app

# Copy systemd service file
echo "Setting up systemd service..."
sudo cp /home/stecher/lunch_app/lunch-app.service /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable lunch-app.service

# Start the service
sudo systemctl start lunch-app.service

# Check status
sudo systemctl status lunch-app.service

echo "Deployment complete!"
echo ""
echo "Useful commands:"
echo "  - Check status: sudo systemctl status lunch-app"
echo "  - View logs: sudo journalctl -u lunch-app -f"
echo "  - Restart service: sudo systemctl restart lunch-app"
echo "  - Stop service: sudo systemctl stop lunch-app"
echo ""
echo "The app should be accessible at http://$(hostname -I | awk '{print $1}'):7000"