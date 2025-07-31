"""
Chrome WebDriver setup for ARM64/aarch64 compatibility.
This module provides a common setup for Chrome WebDriver that works on ARM64 systems.
"""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

logger = logging.getLogger(__name__)


def get_chrome_driver():
    """
    Get a Chrome WebDriver instance configured for ARM64 systems.
    Uses the system-installed ChromeDriver instead of webdriver-manager.
    """
    # Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Use system ChromeDriver (installed via apt)
    # On Debian/Ubuntu ARM64 systems, ChromeDriver is typically at /usr/bin/chromedriver
    service = Service('/usr/bin/chromedriver')
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Successfully created Chrome WebDriver using system ChromeDriver")
        return driver
    except Exception as e:
        logger.error(f"Failed to create Chrome WebDriver: {e}")
        raise