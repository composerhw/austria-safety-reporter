import os
import json
import shutil
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# Configuration
TEMPLATE_DIR = 'templates'
PUBLIC_DIR = 'public'
DATA_DIR = os.path.join(PUBLIC_DIR, 'data')
ARCHIVE_FILE = os.path.join(DATA_DIR, 'archive.json')

class WebGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """Ensure public and data directories exist."""
        os.makedirs(PUBLIC_DIR, exist_ok=True)
        os.makedirs(DATA_DIR, exist_ok=True)
        # Copy styles if exist
        if os.path.exists('public/styles.css'):
            pass # Already in place if we write to public/styles.css
        # If we have static assets in templates/static, copy them (not used yet)

    def load_archive(self):
        """Load the full history of articles."""
        if os.path.exists(ARCHIVE_FILE):
            try:
                with open(ARCHIVE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_archive(self, articles):
        """Save updated archive."""
        with open(ARCHIVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)

    def update_archive(self, new_items):
        """Add new items to the archive, avoiding duplicates."""
        archive = self.load_archive()
        existing_links = {item['link'] for item in archive}
        
        added_count = 0
        for item in new_items:
            if item['link'] not in existing_links:
                # Add a timestamp if missing
                if 'fetched_at' not in item:
                    item['fetched_at'] = datetime.now().isoformat()
                archive.insert(0, item) # Prepend new items
                added_count += 1
        
        self.save_archive(archive)
        print(f"Added {added_count} items to web archive.")
        return archive

    def generate_site(self, current_news):
        """Generate all static pages."""
        # 1. Update Archive
        full_archive = self.update_archive(current_news)
        
        # 2. Generate Index (Home)
        # We display Today's news, or if empty, the latest 20 from archive
        display_items = current_news if current_news else full_archive[:10]
        
        self._render_page('index.html', {
            'news_items': display_items,
            'today_date': datetime.now().strftime("%Y년 %m월 %d일"),
            'current_year': datetime.now().year
        })
        
        # 3. Generate Archive Page
        self._render_page('archive.html', {
            'news_items': full_archive,
            'current_year': datetime.now().year
        })
        
        # 4. Generate Search Page
        self._render_page('search.html', {
            'current_year': datetime.now().year
        })
        
        print("Static site generated in 'public/' directory.")

    def _render_page(self, template_name, context):
        """Render a single template."""
        template = self.env.get_template(template_name)
        output = template.render(context)
        with open(os.path.join(PUBLIC_DIR, template_name), 'w', encoding='utf-8') as f:
            f.write(output)

if __name__ == "__main__":
    # Test run
    gen = WebGenerator()
    gen.generate_site([])
