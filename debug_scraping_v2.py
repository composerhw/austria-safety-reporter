import trafilatura
import requests
from bs4 import BeautifulSoup

urls = [
    "https://ooe.orf.at/stories/3242633/",
    "https://www.kleinezeitung.at/oesterreich/18134321/pilnacek-u-ausschuss-gemeindeaerztin-und-staatsanwaeltin-werden-befragt",
    "https://www.meinbezirk.at/c-lokales/zwei-buben-legten-am-bahnhof-nenzing-feuer_a6498712",
    "https://www.kronenzeitung.at/3232015"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.google.com/'
}

print("--- Testing Scraping V2 ---")
for url in urls:
    print(f"\nURL: {url}")
    try:
        # Method 1: Requests + Trafilatura
        print("Method 1: Requests + Trafilatura")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = trafilatura.extract(response.content, include_comments=False, include_tables=False)
            if result:
                print(f"Success! Length: {len(result)}")
                print(f"Preview: {result[:200].replace(chr(10), ' ')}...")
            else:
                print("Trafilatura returned None")
                # Fallback to BS4
                soup = BeautifulSoup(response.content, 'html.parser')
                ps = soup.find_all('p')
                text = " ".join([p.get_text() for p in ps])
                print(f"BS4 Fallback Length: {len(text)}")
                print(f"BS4 Preview: {text[:200]}...")
        else:
            print("Request failed")

    except Exception as e:
        print(f"Error: {e}")
