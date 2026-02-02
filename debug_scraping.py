import trafilatura
from bs4 import BeautifulSoup
import requests

urls = [
    "https://www.kronenzeitung.at/3232015", # Example URL from user (reconstructed or similar)
    "https://www.meinbezirk.at/c-lokales/zwei-buben-legten-am-bahnhof-nenzing-feuer_a6498712",
    "https://ooe.orf.at/stories/3242633/",
    "https://www.kleinezeitung.at/oesterreich/18134321/pilnacek-u-ausschuss-gemeindeaerztin-und-staatsanwaeltin-werden-befragt"
]

def is_cookie_consent_text(text):
    if not text:
        return False
    cookie_keywords = [
        "cookie", "cookies", "consent", "zustimmen", "akzeptieren", 
        "datenschutz", "privacy policy", "allow all", "alle akzeptieren",
        "wir verwenden cookies", "diese webseite verwendet cookies",
        "personal data", "partners", "advertising", "werbung"
    ]
    lower_text = text.lower()
    keyword_count = 0
    for kw in cookie_keywords:
        if kw in lower_text:
            keyword_count += 1
    
    if len(text) < 500 and keyword_count >= 2:
        return True
    if lower_text.strip().startswith("wir verwenden cookies") or \
       lower_text.strip().startswith("diese webseite verwendet"):
        return True
    return False

print("--- Testing Trafilatura ---")
for url in urls:
    print(f"\nURL: {url}")
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            result = trafilatura.extract(downloaded, include_comments=False, include_tables=False, no_fallback=False)
            if result:
                print(f"Extracted Length: {len(result)}")
                print(f"Is Cookie Text: {is_cookie_consent_text(result)}")
                print(f"Preview: {result[:200]}...")
            else:
                print("Extraction returned None")
        else:
            print("Download failed")
    except Exception as e:
        print(f"Error: {e}")
