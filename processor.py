from deep_translator import GoogleTranslator
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import re
import trafilatura
from googlenewsdecoder import new_decoderv1

class NewsProcessor:
    def __init__(self):
        self.translator = GoogleTranslator(source='auto', target='ko')
        # Trafilatura handles requests internally, but we can keep session if needed later.
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def clean_text(self, text):
        """Remove HTML tags and extra whitespace."""
        if not text:
            return ""
        # Trafilatura already returns clean text, but extra safety
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(separator=" ").strip()

    def is_cookie_consent_text(self, text):
        """Check if the text looks like a cookie consent banner."""
        if not text:
            return False
        
        cookie_keywords = [
            "cookie", "cookies", "consent", "zustimmen", "akzeptieren", 
            "datenschutz", "privacy policy", "allow all", "alle akzeptieren",
            "wir verwenden cookies", "diese webseite verwendet cookies",
            "personal data", "partners", "advertising", "werbung"
        ]
        
        # Check for high density of cookie keywords
        lower_text = text.lower()
        keyword_count = 0
        for kw in cookie_keywords:
            if kw in lower_text:
                keyword_count += 1
        
        # If text is short and has cookie keywords, it's likely a banner
        if len(text) < 500 and keyword_count >= 2:
            return True
            
        # If text starts with typical cookie phrases
        if lower_text.strip().startswith("wir verwenden cookies") or \
           lower_text.strip().startswith("diese webseite verwendet"):
            return True
            
        return False

    def resolve_redirect(self, url):
        """Resolve Google News redirect to get the real article URL using googlenewsdecoder."""
        if "news.google.com" not in url:
            return url
            
        try:
            decoded = new_decoderv1(url)
            if decoded.get("status"):
                return decoded["decoded_url"]
            return url
        except Exception as e:
            # print(f"Error resolving redirect for {url}: {e}")
            return url

    def scrape_article_content(self, url):
        """Attempt to scrape the main content using requests + trafilatura."""
        try:
            # 0. Resolve Redirect (Critical for Google News links)
            final_url = self.resolve_redirect(url)
            # print(f"Resolved {url} -> {final_url}")
            
            # 1. Download with requests (better User-Agent handling)
            response = self.session.get(final_url, timeout=10) # Increased timeout
            if response.status_code != 200:
                return None
            
            # 2. Extract with trafilatura
            result = trafilatura.extract(response.content, include_comments=False, include_tables=False, no_fallback=False)
            
            # 3. Fallback to simple BeautifulSoup
            if not result or len(result) < 100:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Try to find the main article body using common classes/tags
                # This is hard to generalize, but we can try 'article', 'main', or just all 'p'
                
                # Heuristic: Get all p tags, filter by length
                paragraphs = soup.find_all('p')
                content = []
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 60 and not self.is_cookie_consent_text(text):
                        content.append(text)
                
                if content:
                    result = "\n".join(content[:10]) # Take more paragraphs for fallback
            
            if not result:
                return None

            # Check for cookie consent garbage
            if self.is_cookie_consent_text(result):
                return None
                
            # Limit length for summary
            paragraphs = result.split('\n')
            summary_text = ""
            for p in paragraphs:
                if len(summary_text) + len(p) > 1000:
                    break
                if len(p.strip()) > 30:
                    summary_text += p.strip() + " "
            
            return summary_text.strip()
            
        except Exception as e:
            # print(f"Scraping failed for {url}: {e}")
            return None

    def process_news(self, news_items):
        processed_news = []
        print(f"Processing {len(news_items)} news items...")
        
        for item in news_items:
            try:
                # 1. Handle Title and Source Name
                original_title = item['title']
                source_name = item['source']
                
                # Clean Title: Remove " - Source Name" from the end
                title_part = original_title
                # Check if source name is at the end of title
                if source_name and original_title.endswith(source_name):
                    title_part = original_title.replace(f" - {source_name}", "").strip()
                elif " - " in original_title:
                    # Fallback split if source name doesn't match exactly
                    parts = original_title.rsplit(" - ", 1)
                    if len(parts) == 2:
                        title_part = parts[0]

                # Translate Title
                try:
                    title_ko = self.translator.translate(title_part)
                except:
                    title_ko = title_part

                # 2. Get Summary (Scrape or Fallback)
                summary_text = self.scrape_article_content(item['link'])
                
                if not summary_text:
                    # Fallback to RSS summary
                    summary_text = item['summary']
                    # RSS summary often has HTML, clean it
                    summary_text = self.clean_text(summary_text)
                    
                    # RSS summary might also end with " - Source Name" or similar
                    if source_name and source_name in summary_text:
                        summary_text = summary_text.replace(f" - {source_name}", "")
                        summary_text = summary_text.replace(source_name, "") # Risky but prevents "Small Newspaper"

                # Translate Summary
                summary_ko = ""
                if summary_text:
                    # Clean up any remaining source name occurrences at the end
                    # (Simple heuristic)
                    
                    # Limit length for translation
                    if len(summary_text) > 1000:
                        summary_text = summary_text[:1000] + "..."
                    
                    try:
                        summary_ko = self.translator.translate(summary_text)
                    except Exception as e:
                        print(f"Translation error for summary: {e}")
                        summary_ko = ""

                processed_item = {
                    'original_title': original_title,
                    'title_ko': title_ko,
                    'link': item['link'],
                    'published': item['published'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(item['published'], datetime) else str(item['published']),
                    'source': source_name,
                    'summary_ko': summary_ko,
                    'keyword': item['keyword']
                }
                processed_news.append(processed_item)
                print(f"Processed: {title_ko} ({source_name})")
                
            except Exception as e:
                print(f"Error processing item {item['title']}: {e}")
                
        return processed_news

if __name__ == "__main__":
    # Test with dummy data
    processor = NewsProcessor()
    dummy_news = [{
        'title': 'Unfall auf der A1',
        'link': 'http://example.com',
        'published': datetime.now(),
        'source': 'Test Source',
        'summary': 'Ein schwerer Unfall hat sich ereignet.',
        'keyword': 'Unfall'
    }]
    print(processor.process_news(dummy_news))
