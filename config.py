"""
Tubayo Hotel Scraper — Configuration File
==========================================
Add or remove hotel URLs here without touching the main scraper code.
"""

# ── REQUEST SETTINGS ──
DELAY_BETWEEN_REQUESTS = 3      # seconds between requests (be respectful)
REQUEST_TIMEOUT = 15            # seconds before giving up on a page
MAX_RETRIES = 2                 # number of retries on failure

# ── OUTPUT SETTINGS ──
OUTPUT_FORMAT = ["csv", "json"]  # options: "csv", "json"
OUTPUT_FOLDER = "output"         # folder to save results

# ── HOTEL URLS TO SCRAPE ──
HOTEL_URLS = [
    # ── KAMPALA ──
    "https://www.eminpasha.com",
    "https://www.spekehotel.com",
    "https://www.fairwayhotel.co.ug",
    "https://www.golfcoursehotel.co.ug",
    "https://www.imperialhotels.co.ug",
    "https://www.africanahotel.com",
    "https://www.kabira.co.ug",
    "https://www.humuraresorts.com",
    "https://www.cassialore.com",

    # ── ENTEBBE ──
    "https://www.laico-lakevictor.com",
    "https://www.pearlofafrica.com",

    # ── JINJA ──
    "https://www.jinjanileresort.com",
    "https://www.sourcenilehotel.com",

    # ── WESTERN UGANDA ──
    "https://www.nkuringobwindi.com",
    "https://www.ihamba.com",
    "https://www.budongosafarilodge.com",

    # ── ADD MORE URLS BELOW ──
    # "https://www.yourhotel.com",
]

# ── ROOM KEYWORDS ──
ROOM_KEYWORDS = [
    'standard', 'deluxe', 'suite', 'executive', 'superior',
    'double', 'single', 'twin', 'family', 'presidential',
    'junior', 'penthouse', 'studio', 'apartment', 'cottage',
    'lodge', 'villa', 'bungalow', 'chalet'
]

# ── AMENITY KEYWORDS ──
AMENITY_KEYWORDS = [
    'wifi', 'wi-fi', 'internet', 'pool', 'swimming', 'gym',
    'fitness', 'spa', 'restaurant', 'bar', 'parking',
    'air conditioning', 'ac', 'tv', 'television', 'breakfast',
    'laundry', 'conference', 'meeting room', 'airport shuttle',
    'generator', 'security', 'rooftop'
]
