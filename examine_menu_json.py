# examine_menu_json.py
import json
import pprint

def examine_json_structure():
    """Examine the structure of the extracted JSON data."""
    try:
        with open('menu_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print("🔍 Examining JSON structure")
        print("=" * 60)
        
        # Print the full structure with pretty printing
        pp = pprint.PrettyPrinter(indent=2, width=100)
        
        print("\n📋 Top-level keys:")
        print(list(data.keys()))
        
        print("\n📋 Page Props:")
        if 'props' in data and 'pageProps' in data['props']:
            page_props = data['props']['pageProps']
            print("Keys in pageProps:", list(page_props.keys()))
            
            # Save for detailed inspection
            with open('page_props.json', 'w', encoding='utf-8') as f:
                json.dump(page_props, f, indent=2, ensure_ascii=False)
            print("\n💾 Saved pageProps to 'page_props.json' for detailed inspection")
            
        print("\n📋 Full structure preview:")
        # Convert to string to see structure
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        print(json_str[:2000] + "..." if len(json_str) > 2000 else json_str)
        
    except FileNotFoundError:
        print("❌ menu_data.json not found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    examine_json_structure()
