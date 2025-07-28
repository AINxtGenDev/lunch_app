# analyze_iframe_content.py
from bs4 import BeautifulSoup
import re
import json

def analyze_iframe_structure():
    """Analyze the structure of the saved iframe content."""
    print("🔍 Analyzing Erste Campus iframe structure")
    print("=" * 60)
    
    try:
        with open('erste_campus_iframe_content.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 1. Look for any script tags with JSON data
        print("\n📋 Checking for JSON data in scripts...")
        scripts = soup.find_all('script')
        for i, script in enumerate(scripts):
            if script.string and ('menu' in script.string.lower() or 'meal' in script.string.lower()):
                print(f"\n  Script {i+1} contains menu-related data:")
                print(script.string[:200] + "..." if len(script.string) > 200 else script.string)
                
                # Try to extract JSON
                json_pattern = re.search(r'({.*}|\[.*\])', script.string, re.DOTALL)
                if json_pattern:
                    try:
                        data = json.loads(json_pattern.group(1))
                        print(f"  ✅ Valid JSON found with {len(data)} items")
                        with open('menu_data.json', 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        print("  💾 Saved to menu_data.json")
                    except:
                        pass
        
        # 2. Analyze the HTML structure
        print("\n📋 Analyzing HTML structure...")
        
        # Find all elements with text content
        all_elements = soup.find_all(text=True)
        text_content = [text.strip() for text in all_elements if text.strip() and len(text.strip()) > 10]
        
        print(f"\n  Found {len(text_content)} text elements")
        print("\n  Sample content:")
        for i, text in enumerate(text_content[:20]):  # Show first 20
            print(f"  {i+1}. {text[:80]}...")
            
        # 3. Look for specific patterns
        print("\n📋 Looking for menu patterns...")
        
        # Date patterns
        date_elements = soup.find_all(text=re.compile(r'\d{1,2}\.\d{1,2}\.\d{4}'))
        print(f"\n  Found {len(date_elements)} date patterns")
        
        # Price patterns
        price_elements = soup.find_all(text=re.compile(r'€\s*\d+[,.]?\d*'))
        print(f"  Found {len(price_elements)} price patterns")
        
        # 4. Check for specific class names and IDs
        print("\n📋 Checking for specific classes and IDs...")
        
        # Find all unique classes
        all_classes = set()
        for element in soup.find_all(class_=True):
            if isinstance(element['class'], list):
                all_classes.update(element['class'])
            else:
                all_classes.add(element['class'])
                
        print(f"\n  Unique classes found: {sorted(all_classes)}")
        
        # Find all unique IDs
        all_ids = set()
        for element in soup.find_all(id=True):
            all_ids.add(element['id'])
            
        print(f"\n  Unique IDs found: {sorted(all_ids)}")
        
        # 5. Look for container structures
        print("\n📋 Analyzing container structures...")
        
        # Common container tags
        for tag in ['div', 'section', 'article', 'table', 'ul', 'ol']:
            containers = soup.find_all(tag)
            if containers:
                print(f"\n  {tag} elements: {len(containers)}")
                for i, container in enumerate(containers[:3]):
                    text = container.get_text(strip=True)
                    if len(text) > 20:
                        print(f"    {i+1}. {text[:100]}...")
                        
        # 6. Save a pretty-printed version
        with open('erste_campus_iframe_pretty.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("\n💾 Saved pretty-printed HTML to 'erste_campus_iframe_pretty.html'")
        
    except FileNotFoundError:
        print("❌ erste_campus_iframe_content.html not found. Run the scraper first.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    analyze_iframe_structure()
