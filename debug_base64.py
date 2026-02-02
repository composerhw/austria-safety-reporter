import base64
import functools
import re
import requests

def decode_google_news_url(url):
    """
    Decodes the base64 URL from Google News.
    Google News URLs are often in the format:
    https://news.google.com/rss/articles/BASE64_STRING?oc=5
    
    The base64 string usually contains the target URL, often with some binary prefix/suffix.
    """
    try:
        # Extract the base64 part
        match = re.search(r'articles/([a-zA-Z0-9\-_]+)', url)
        if not match:
            return None
            
        b64_str = match.group(1)
        
        # Fix padding
        padding = len(b64_str) % 4
        if padding:
            b64_str += '=' * (4 - padding)
            
        # Decode (URL-safe)
        decoded_bytes = base64.urlsafe_b64decode(b64_str)
        
        # The decoded bytes usually contain the URL mixed with binary data.
        # We can try to find the URL using regex or parsing.
        # Common pattern: The URL starts after some binary header and ends before some binary footer.
        # It often starts with http or https.
        
        # Convert to string with 'latin-1' to preserve bytes as chars
        decoded_str = decoded_bytes.decode('latin-1')
        
        # Find URL pattern
        url_match = re.search(r'(https?://[a-zA-Z0-9\-\._~:/?#\[\]@!$&\'()*+,;=%]+)', decoded_str)
        if url_match:
            return url_match.group(1)
            
        # Sometimes it's a bit more complex (protobuf-like).
        # Let's try a simpler heuristic: find the longest string starting with http
        parts = re.findall(r'(https?://[^\x00-\x1F\x7F]+)', decoded_str)
        if parts:
            # Return the longest one, as it's likely the full URL
            return max(parts, key=len)
            
        return None
        
    except Exception as e:
        print(f"Decoding error: {e}")
        return None

# Test URLs
urls = [
    "https://news.google.com/rss/articles/CBMiS0FVX3lxTFBGLURvUk9iSUZ3MkJSbGxvQ09YM0NEN2tEaEE3MVJQZnk1YzRicERsWjdadjdHQ2k5LUt2emFHQll4OEZ5bklRWEE1SQ?oc=5",
    "https://news.google.com/rss/articles/CBMiQkFVX3lxTE5RUU9scnl1WUlzU0NfbDdLb0htN0tTU0VyUVowVjJSVGVMWnBnSktXdFJfZXdzUTJseWJXLTIxNzF2QQ?oc=5"
]

print("--- Testing Base64 Decoding ---")
for url in urls:
    decoded = decode_google_news_url(url)
    print(f"\nOriginal: {url}")
    print(f"Decoded:  {decoded}")
    
    if decoded:
        try:
            # Verify connectivity
            r = requests.head(decoded, timeout=5, allow_redirects=True)
            print(f"Status: {r.status_code}")
        except Exception as e:
            print(f"Verification failed: {e}")
