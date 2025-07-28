# view_iframe_content.py
def view_iframe_content():
    """Display the raw content of the iframe."""
    try:
        with open('erste_campus_iframe_content.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Print first 2000 characters to see the structure
        print("📄 First 2000 characters of iframe content:")
        print("=" * 60)
        print(content[:2000])
        print("\n" + "=" * 60)
        
        # Look for specific keywords
        keywords = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 
                   'montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag',
                   'soup', 'suppe', 'menu', 'dish', 'gericht', '€', 'euro']
        
        print("\n🔍 Keyword search:")
        for keyword in keywords:
            count = content.lower().count(keyword.lower())
            if count > 0:
                print(f"  '{keyword}': found {count} times")
                
                # Show context
                index = content.lower().find(keyword.lower())
                if index != -1:
                    start = max(0, index - 50)
                    end = min(len(content), index + 100)
                    context = content[start:end].replace('\n', ' ')
                    print(f"    Context: ...{context}...")
                    
    except FileNotFoundError:
        print("❌ erste_campus_iframe_content.html not found.")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    view_iframe_content()
