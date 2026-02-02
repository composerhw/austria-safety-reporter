import requests
import re

google_news_url = "https://news.google.com/rss/articles/CBMiS0FVX3lxTFBGLURvUk9iSUZ3MkJSbGxvQ09YM0NEN2tEaEE3MVJQZnk1YzRicERsWjdadjdHQ2k5LUt2emFHQll4OEZ5bklRWEE1SQ?oc=5"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

print(f"Testing URL: {google_news_url}")

try:
    response = requests.get(google_news_url, headers=headers, allow_redirects=True, timeout=10)
    print(f"Final URL: {response.url}")
    print(f"Status Code: {response.status_code}")
    print(f"History: {response.history}")
    
    print("\n--- Content Preview (First 1000 chars) ---")
    print(response.text[:1000])
    
    # Check for common redirect patterns in HTML
    if "window.location" in response.text:
        print("\n[!] Found 'window.location' in text - likely JS redirect.")
    if "Opening" in response.text:
        print("\n[!] Found 'Opening' in text - Google News intermediate page.")

except Exception as e:
    print(f"Error: {e}")
