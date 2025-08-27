# Raspberry Pi Setup for Cyclist Scraper

## Installation Steps

1. **Install System Dependencies**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-deu
sudo apt-get install -y chromium-browser chromium-chromedriver
```

2. **Install Python Dependencies**
```bash
conda activate lunch-menu-app
pip install pytesseract pillow
```

3. **Create Screenshots Directory**
```bash
mkdir -p /home/stecher/lunch_app/Screenshots
```

## Files to Update

Copy these files to your Raspberry Pi at `/home/stecher/lunch_app/`:

### Modified Files:
- `app/scrapers/cyclist_scraper_enhanced.py` - Fixed base_url and Selenium issues
- `app/services/scraping_service.py` - Uses enhanced scraper
- `environment.yaml` - Added pytesseract and pillow
- `test_cyclist_scraper.py` - Saves to Screenshots directory

### New Files:
- `app/scrapers/cyclist_scraper_improved.py` - Better OCR processing
- `app/scrapers/cyclist_scraper_simple_ocr.py` - No Selenium required
- `setup_raspberry_pi.sh` - Setup script

## Testing

1. **Test with the improved scraper (recommended for Raspberry Pi):**
```bash
# Edit scraping_service.py to use the improved version:
# from app.scrapers.cyclist_scraper_improved import CyclistScraperImproved
# Then in scrapers list: CyclistScraperImproved()

python test_cyclist_scraper.py
```

2. **Check the Screenshots directory for debugging:**
```bash
ls -la /home/stecher/lunch_app/Screenshots/
```

Files created:
- `original_menu.png` - Original downloaded image
- `preprocessed_menu.png` - Processed image for OCR
- `ocr_output.txt` - Raw OCR text output
- `test_menu_image.png` - Test screenshot
- `test_ocr_output.txt` - Test OCR output

## Troubleshooting

### If OCR quality is poor:

1. **Use the fallback menu** - The scraper will automatically use hardcoded menu if OCR fails

2. **Manually update the Flipsnack URL** in `cyclist_scraper_improved.py`:
```python
known_url = "https://www.flipsnack.com/EE9BE6CC5A8/[new-menu-url]/full-view.html"
```

3. **Place a clean screenshot** of the menu in Screenshots directory and run OCR test:
```bash
python test_cyclist_scraper.py
# Choose option 2 for OCR test
```

### If Selenium fails on ARM:

Use `cyclist_scraper_improved.py` or `cyclist_scraper_simple_ocr.py` instead of the enhanced version.

## Production Deployment

For production, use the improved scraper which doesn't require Selenium:

```python
# In app/services/scraping_service.py
from app.scrapers.cyclist_scraper_improved import CyclistScraperImproved

# In the scrapers list:
self.scrapers = [
    # ... other scrapers ...
    CyclistScraperImproved(),  # Instead of CyclistScraperEnhanced
]
```

## Notes

- OCR processing is slower on Raspberry Pi - be patient
- The scraper will fall back to hardcoded menu if OCR fails
- Screenshots are saved for debugging in `/home/stecher/lunch_app/Screenshots/`
- Update the hardcoded fallback menu weekly in the scraper files