# Configuration for Austria Safety News Reporter

# News Sources (Google News RSS)
# hl=de-AT: German language, Austria region
# gl=AT: Austria location
# ceid=AT:de: Country and language identifier
GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss/search?q={query}&hl=de-AT&gl=AT&ceid=AT:de"

# Search Keywords (German)
# Focused on safety, accidents, police reports, warnings, strikes, natural disasters
SEARCH_KEYWORDS = [
    "Unfall",           # Accident
    "Polizei",          # Police
    "Feuer",            # Fire
    "Brand",            # Fire/Blaze
    "Diebstahl",        # Theft
    "Raub",             # Robbery
    "Warnung",          # Warning
    "Sicherheit",       # Safety
    "Verbrechen",       # Crime
    "Vermisst",         # Missing person
    "Lawine",           # Avalanche
    "Unwetter",         # Severe weather
    "Demonstration",    # Demonstration/Protest
    "Streik",           # Strike (Transport strikes etc.)
    "Straßensperre",    # Road closure
    "ÖBB",              # Austrian Federal Railways (delays/issues)
    "Wiener Linien"     # Vienna Public Transport
]

# Keywords to EXCLUDE (to filter out Germany, Switzerland, etc.)
EXCLUDED_KEYWORDS = [
    "Deutschland", "Berlin", "München", "Hamburg", "Frankfurt", "Köln", # Germany
    "Schweiz", "Zürich", "Bern", "Genf", "Basel", # Switzerland
    "Bundesrepublik", "DB", "Deutsche Bahn",
    "Bayern", "Sachsen", "NRW"
]

# Allowed Sources (Whitelist)
# Only news from these sources will be included.
ALLOWED_SOURCES = [
    # Nationwide
    "ORF", "Der Standard", "Die Presse", "Kurier", "Kronen Zeitung", 
    "Heute", "OE24", "Puls 24", "Salzburger Nachrichten", "Wiener Zeitung",
    
    # Regional
    "Kleine Zeitung", "Tiroler Tageszeitung", "OÖN", "Oberösterreichische Nachrichten",
    "Vorarlberger Nachrichten", "NÖN", "Niederösterreichische Nachrichten",
    "BVZ", "Burgenländische Volkszeitung", "MeinBezirk", "MeinBezirk.at", "Vol.at",
    "5min.at", "Vienna.at",
    
    # Government / Official / Specialized
    "Polizei", "LPD", "Landespolizeidirektion", "BMI", "Bundesministerium für Inneres",
    "Stadt Wien", "APA-OTS", "APA", "ÖAMTC", "ARBÖ", "Asfinag"
]

# Date filtering
DAYS_LOOKBACK = 1  # Fetch news from the last N days (kept for fetcher optimization, but strict 24h check applied later)

# Output
OUTPUT_DIR = "reports"
# New format: yyyymmdd Safety Report
FILENAME_FORMAT = "{date} Safety Report" 
DATE_FORMAT = "%Y%m%d"

# History file for deduplication
HISTORY_FILE = "news_history.json"
