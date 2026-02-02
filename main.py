import os
import sys
import json
from fetcher import NewsFetcher
from processor import NewsProcessor
from reporter import PDFReporter
from web_generator import WebGenerator
from datetime import datetime
from config import HISTORY_FILE

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_history(history_set):
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(list(history_set), f)
    except Exception as e:
        print(f"Error saving history: {e}")

def main():
    print(f"--- Austria Safety News Reporter Started at {datetime.now()} ---")
    
    # Check if running in GitHub Actions
    is_github_action = os.getenv('GITHUB_ACTIONS') == 'true'
    
    # Load history (Local Deduplication)
    history = load_history()
    print(f"Loaded {len(history)} items from history.")

    # 1. Fetch News
    try:
        fetcher = NewsFetcher()
        news_items = fetcher.fetch_news()
        
        # Deduplication for New Processing
        new_items = []
        for item in news_items:
            # We check if link is in local history OR if we want to re-process for web
            # The web generator uses data/archive.json, but main.py uses news_history.json
            # Ideally they should be synced or unified. 
            # For now, we rely on news_history.json to avoid re-translating (costly/slow).
            if item['link'] not in history:
                new_items.append(item)
        
        print(f"Found {len(new_items)} new items after deduplication.")
        
    except Exception as e:
        print(f"Critical Error in Fetcher: {e}")
        return

    # 2. Process News (Translate & Summarize)
    processed_news = []
    try:
        if new_items:
            processor = NewsProcessor()
            processed_news = processor.process_news(new_items)
            
            # Update history
            for item in new_items:
                history.add(item['link'])
            save_history(history)
        else:
            print("No new items to process.")
            
    except Exception as e:
        print(f"Critical Error in Processor: {e}")
        return

    # 3. Generate Static Website (Priority)
    print("Generating Static Website...")
    web_gen = WebGenerator()
    web_gen.generate_site(processed_news)


    # 4. Generate PDF (Optional / Local only)
    if processed_news:
        try:
            reporter = PDFReporter()
            pdf_path = reporter.generate_report(processed_news)
            txt_path = reporter.generate_txt_report(processed_news)
            
            if pdf_path and not is_github_action:
                print(f"PDF Report: {pdf_path}")
                os.system(f"open '{pdf_path}'")
                
        except Exception as e:
            print(f"Error in PDF Reporter: {e}")

    print(f"--- Finished at {datetime.now()} ---")

if __name__ == "__main__":
    main()
