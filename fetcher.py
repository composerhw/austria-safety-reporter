import feedparser
import requests
from datetime import datetime, timedelta
import time
from config import GOOGLE_NEWS_RSS_URL, SEARCH_KEYWORDS, DAYS_LOOKBACK, EXCLUDED_KEYWORDS, ALLOWED_SOURCES
from urllib.parse import quote, urlparse

class NewsFetcher:
    def __init__(self):
        self.seen_links = set()

    def is_allowed_source(self, source_name, link):
        """Check if the source is in the whitelist or if the domain matches a whitelist source."""
        if not source_name:
            return False
            
        # Check exact or partial match in source name
        for allowed in ALLOWED_SOURCES:
            if allowed.lower() in source_name.lower():
                return True
        
        # Fallback: Check domain if source name is generic or missing, 
        # but for now let's stick to the source name provided by Google News 
        # as it's usually reliable for major outlets.
        # We can also check if the allowed source name appears in the domain.
        try:
            domain = urlparse(link).netloc.lower()
            for allowed in ALLOWED_SOURCES:
                # Remove spaces for domain check (e.g. "Die Presse" -> "diepresse")
                clean_allowed = allowed.lower().replace(" ", "").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
                if clean_allowed in domain:
                    return True
        except:
            pass
            
        return False

    def contains_excluded_keyword(self, text):
        """Check if text contains any excluded keywords"""
        if not text:
            return False
        for keyword in EXCLUDED_KEYWORDS:
            if keyword.lower() in text.lower():
                return True
        return False

    def fetch_news(self):
        all_news = []
        cutoff_date = datetime.now() - timedelta(days=DAYS_LOOKBACK)
        
        print(f"Fetching news since {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')} (Strict 24h window)...")

        for keyword in SEARCH_KEYWORDS:
            print(f"Searching for: {keyword}")
            encoded_query = quote(keyword)
            rss_url = GOOGLE_NEWS_RSS_URL.format(query=encoded_query)
            
            try:
                feed = feedparser.parse(rss_url)
                
                if feed.bozo:
                    print(f"Error parsing feed for {keyword}: {feed.bozo_exception}")
                    continue

                for entry in feed.entries:
                    # Parse published date
                    try:
                        published_parsed = entry.published_parsed
                        published_dt = datetime.fromtimestamp(time.mktime(published_parsed))
                    except Exception as e:
                        print(f"Error parsing date for {entry.title}: {e}")
                        continue

                    # STRICT 24-HOUR FILTER
                    # Calculate time difference
                    time_diff = datetime.now() - published_dt
                    if time_diff > timedelta(hours=24):
                        # print(f"Skipping old news: {entry.title} ({time_diff})")
                        continue
                        
                    if entry.link in self.seen_links:
                        continue

                    source_name = entry.source.title if hasattr(entry, 'source') else 'Unknown'
                    
                    # FILTER 1: Whitelist Check
                    if not self.is_allowed_source(source_name, entry.link):
                        # print(f"Skipping not allowed source: {source_name}")
                        continue

                    # FILTER 2: Excluded Keywords in Title
                    if self.contains_excluded_keyword(entry.title):
                        # print(f"Skipping excluded topic: {entry.title}")
                        continue

                    self.seen_links.add(entry.link)
                    
                    news_item = {
                        'title': entry.title,
                        'link': entry.link,
                        'published': published_dt,
                        'source': source_name,
                        'summary': entry.summary if hasattr(entry, 'summary') else '',
                        'keyword': keyword
                    }
                    all_news.append(news_item)
                    
            except Exception as e:
                print(f"Error fetching news for {keyword}: {e}")
                
        print(f"Total news found (after strict filtering): {len(all_news)}")
        # Sort by date, newest first
        all_news.sort(key=lambda x: x['published'], reverse=True)
        return all_news

if __name__ == "__main__":
    fetcher = NewsFetcher()
    news = fetcher.fetch_news()
    for item in news[:5]:
        print(f"[{item['published']}] {item['title']} - {item['link']}")
