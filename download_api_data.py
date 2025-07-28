# download_api_data.py
import requests
import json
import pprint

def download_and_examine_api():
    """Download and examine the API response."""
    api_url = "https://erstecampus.at/mealplan/2025/_next/data/X9scG9sCeIjXjqy-lGqF1/external/single/kantine-en.json"

    print(f"📥 Downloading data from API endpoint...")
    print(f"URL: {api_url}")
    print("=" * 60)

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://erstecampus.at/mealplan/2025/external/single/kantine-en.html',
        }

        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Save the full response
        with open('api_response.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("💾 Saved full API response to 'api_response.json'")

        # Examine structure
        print("\n📋 API Response Structure:")
        print(f"Top-level keys: {list(data.keys())}")

        # Look for pageProps
        if 'pageProps' in data:
            page_props = data['pageProps']
            print(f"\nPageProps keys: {list(page_props.keys())}")

            # Save pageProps separately
            with open('api_page_props.json', 'w', encoding='utf-8') as f:
                json.dump(page_props, f, indent=2, ensure_ascii=False)
            print("💾 Saved pageProps to 'api_page_props.json'")

            # Look for menu-related keys
            for key in page_props:
                value = page_props[key]
                print(f"\n🔍 pageProps['{key}']:")
                if isinstance(value, (dict, list)):
                    print(f"  Type: {type(value).__name__}")
                    if isinstance(value, dict):
                        print(f"  Keys: {list(value.keys())[:10]}")  # First 10 keys
                    elif isinstance(value, list):
                        print(f"  Length: {len(value)}")
                        if value and isinstance(value[0], dict):
                            print(f"  First item keys: {list(value[0].keys())}")
                else:
                    print(f"  Value: {str(value)[:100]}")

        # Look for potential menu data anywhere in the response
        print("\n🔍 Searching for menu-related data...")
        menu_keywords = ['menu', 'meal', 'dish', 'food', 'lunch', 'speise', 'essen']

        def search_for_keywords(obj, path="", depth=0):
            if depth > 5:
                return

            if isinstance(obj, dict):
                for key, value in obj.items():
                    key_lower = str(key).lower()
                    if any(keyword in key_lower for keyword in menu_keywords):
                        print(f"\n  Found '{key}' at {path}.{key}")
                        if isinstance(value, list) and len(value) > 0:
                            print(f"    List with {len(value)} items")
                            if isinstance(value[0], dict):
                                print(f"    First item: {list(value[0].keys())}")
                        elif isinstance(value, dict):
                            print(f"    Dict with keys: {list(value.keys())[:5]}")

                    search_for_keywords(value, f"{path}.{key}", depth + 1)

            elif isinstance(obj, list) and len(obj) > 0:
                search_for_keywords(obj[0], f"{path}[0]", depth + 1)

        search_for_keywords(data)

        # Pretty print a sample
        print("\n📋 Sample of API response (first 1000 chars):")
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        print(json_str[:1000] + "..." if len(json_str) > 1000 else json_str)

    except requests.RequestException as e:
        print(f"❌ Failed to download: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    download_and_examine_api()
