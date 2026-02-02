from googlenewsdecoder import new_decoderv1
import requests

urls = [
    "https://news.google.com/rss/articles/CBMiS0FVX3lxTFBGLURvUk9iSUZ3MkJSbGxvQ09YM0NEN2tEaEE3MVJQZnk1YzRicERsWjdadjdHQ2k5LUt2emFHQll4OEZ5bklRWEE1SQ?oc=5",
    "https://news.google.com/rss/articles/CBMiQkFVX3lxTE5RUU9scnl1WUlzU0NfbDdLb0htN0tTU0VyUVowVjJSVGVMWnBnSktXdFJfZXdzUTJseWJXLTIxNzF2QQ?oc=5"
]

print("--- Testing GoogleNewsDecoder ---")
for url in urls:
    print(f"\nOriginal: {url}")
    try:
        decoded_url = new_decoderv1(url)
        if decoded_url.get("status"):
             final_url = decoded_url["decoded_url"]
             print(f"Decoded: {final_url}")
             
             # Verify connectivity
             try:
                 r = requests.head(final_url, timeout=5, allow_redirects=True)
                 print(f"Status: {r.status_code}")
             except Exception as e:
                 print(f"Verification failed: {e}")
        else:
            print("Decoding failed")
    except Exception as e:
        print(f"Error: {e}")
