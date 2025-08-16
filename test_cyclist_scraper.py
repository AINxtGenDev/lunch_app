#!/usr/bin/env python3
"""Test script for the enhanced Cyclist scraper."""

import sys
import os
import logging
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def test_cyclist_scraper():
    """Test the improved Cyclist scraper with OCR capabilities."""

    from app.scrapers.cyclist_scraper_improved import CyclistScraperImproved

    print("\n" + "=" * 60)
    print("Testing Improved Cyclist Scraper with OCR")
    print("=" * 60 + "\n")
    
    # Create Screenshots directory if it doesn't exist
    screenshots_dir = "/home/stecher/lunch_app/Screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
        print(f"Created directory: {screenshots_dir}")

    # Create scraper instance
    scraper = CyclistScraperImproved()

    # Test 1: Find latest menu URL
    print("Step 1: Finding latest menu image URL...")
    image_url = scraper.get_direct_image_url()
    if image_url:
        print(f"✅ Found image URL: {image_url}")
    else:
        print("❌ Could not find image URL")
        print("   Will use fallback menu")

    # Test 2: Download image (if URL found)
    image_data = None
    if image_url:
        print("\nStep 2: Downloading menu image...")
        try:
            import requests
            browser_headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Referer': 'https://www.flipsnack.com/',
            }
            response = requests.get(image_url, headers=browser_headers, timeout=20)
            if response.status_code == 200:
                image_data = response.content
                print(f"✅ Downloaded image ({len(image_data)} bytes)")
            else:
                print(f"❌ Failed to download: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Download error: {e}")
    if image_data:
        # Save image for debugging in Screenshots directory
        image_path = os.path.join(screenshots_dir, "test_menu_image.png")
        with open(image_path, "wb") as f:
            f.write(image_data)
        print(f"   Saved to {image_path} for inspection")
        
        # Test 3: Perform OCR
        print("\nStep 3: Performing advanced OCR...")
        text = scraper.perform_advanced_ocr(image_data)
        if text:
            print(f"✅ OCR extracted {len(text)} characters")

            # Save OCR text for debugging in Screenshots directory
            ocr_output_path = os.path.join(screenshots_dir, "test_ocr_output.txt")
            with open(ocr_output_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"   Saved OCR output to {ocr_output_path}")

            # Parse menu with intelligent parsing
            print("\nStep 3.5: Parsing menu text...")
            menu_by_day = scraper.parse_menu_intelligently(text)
            print(f"   Found menu for {len(menu_by_day)} days")
            for day in menu_by_day:
                print(f"   - {day}: {len(menu_by_day[day])} items")
        else:
            print("❌ OCR failed")
    else:
        print("\n⚠️ No image data available, will use fallback menu")

    # Test 4: Full scrape
    print("\nStep 4: Running full scrape...")
    menu_items = scraper.scrape()

    if menu_items:
        print(f"✅ Successfully scraped {len(menu_items)} menu items")
        print("\nToday's Menu:")
        print("-" * 40)
        for item in menu_items:
            print(f"• {item['description']}")
            if item.get("price"):
                print(f"  Price: {item['price']}")
    else:
        print("❌ No menu items found")

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60 + "\n")

    return menu_items


def test_ocr_only():
    """Test just the OCR functionality with a local image."""

    from app.scrapers.cyclist_scraper_improved import CyclistScraperImproved
    from PIL import Image
    import pytesseract

    print("\n" + "=" * 60)
    print("Testing OCR with Local Screenshot")
    print("=" * 60 + "\n")
    
    # Create Screenshots directory if it doesn't exist
    screenshots_dir = "/home/stecher/lunch_app/Screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
        print(f"Created directory: {screenshots_dir}")

    screenshot_path = os.path.join(screenshots_dir, "Screenshot from 2025-08-16 09-45-42.png")

    if not os.path.exists(screenshot_path):
        print(f"❌ Screenshot not found: {screenshot_path}")
        return

    print(f"Loading image: {screenshot_path}")

    # Load and process image
    try:
        image = Image.open(screenshot_path)
        print(f"✅ Image loaded: {image.size[0]}x{image.size[1]} pixels")

        # Perform OCR
        scraper = CyclistScraperImproved()

        with open(screenshot_path, "rb") as f:
            image_data = f.read()

        text = scraper.perform_advanced_ocr(image_data)

        if text:
            print(f"✅ OCR extracted {len(text)} characters")

            # Save and display results in Screenshots directory
            ocr_output_path = os.path.join(screenshots_dir, "screenshot_ocr_output.txt")
            with open(ocr_output_path, "w", encoding="utf-8") as f:
                f.write(text)

            print("\nExtracted Text Preview:")
            print("-" * 40)
            print(text[:500] + "..." if len(text) > 500 else text)

            # Parse menu
            menu_by_day = scraper.parse_menu_intelligently(text)

            print("\nParsed Menu by Day:")
            print("-" * 40)
            for day, items in menu_by_day.items():
                print(f"\n{day}:")
                for item in items:
                    print(f"  • {item['name']}")
        else:
            print("❌ OCR failed")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import pytesseract
        from PIL import Image
        import requests
        from bs4 import BeautifulSoup
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("\nPlease install required packages:")
        print("  conda activate lunch-menu-app")
        print("  pip install pytesseract pillow")
        print("\nAlso ensure tesseract-ocr is installed:")
        print("  sudo apt-get install tesseract-ocr tesseract-ocr-deu")
        sys.exit(1)

    # Run tests
    print("Choose test option:")
    print("1. Test full scraper (web + OCR)")
    print("2. Test OCR with local screenshot")
    print("3. Run both tests")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        test_cyclist_scraper()
    elif choice == "2":
        test_ocr_only()
    elif choice == "3":
        test_ocr_only()
        test_cyclist_scraper()
    else:
        print("Invalid choice. Running both tests...")
        test_ocr_only()
        test_cyclist_scraper()
