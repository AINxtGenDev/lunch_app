#!/bin/bash

echo "=== Checking Auto-Start Configuration ==="
echo ""

echo "1. Service status:"
sudo systemctl status lunch-app --no-pager
echo ""

echo "2. Is service enabled for auto-start?"
sudo systemctl is-enabled lunch-app
echo ""

echo "3. List of enabled services (grep for lunch-app):"
sudo systemctl list-unit-files --type=service --state=enabled | grep lunch-app
echo ""

echo "4. Dependencies and targets:"
sudo systemctl show lunch-app --property=Wants,After,WantedBy
echo ""

echo "5. If service is NOT enabled, enable it:"
if ! sudo systemctl is-enabled lunch-app > /dev/null 2>&1; then
    echo "Service is NOT enabled. Enabling now..."
    sudo systemctl enable lunch-app
    echo "Service enabled for auto-start."
else
    echo "Service is already enabled for auto-start."
fi
echo ""

echo "6. Testing restart simulation:"
echo "Current service status before restart test:"
sudo systemctl is-active lunch-app
echo ""

echo "=== Instructions ==="
echo "If the service shows 'enabled', it will start automatically on boot."
echo "To test: sudo reboot (the service should start automatically)"
echo "To check after reboot: sudo systemctl status lunch-app"