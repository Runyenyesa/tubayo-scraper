"""
Tubayo Hotel Web Scraper
========================
Scrapes hotel room info from Ugandan hotel websites.
Outputs structured CSV and JSON ready for Tubayo onboarding.

Usage:
    python tubayo_scraper.py

Author: Lincon - Tubayo Operations Lead
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import re
from datetime import datetime

# ── HEADERS (mimic real browser to avoid blocks) ──
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ── UGANDAN HOTEL URLS TO SCRAPE ──
HOTEL_URLS = [
    "https://www.eminpasha.com",
    "https://www.spekehotel.com",
    "https://www.fairwayhotel.co.ug",
    "https://www.pearlofafrica.com",
    "https://www.golfcoursehotel.co.ug",
    "https://www.imperialhotels.co.ug",
    "https://www.cassialore.com",
    "https://www.affordablehotelsafrica.com",
    "https://www.kabira.co.ug",
    "https://www.humuraresorts.com",
]

# ── KEYWORDS FOR SMART FIELD DETECTION ──
PRICE_PATTERNS = [
    r'UGX[\s]*[\d,]+',
    r'USD[\s]*[\d,]+',
    r'\$[\d,]+',
    r'[\d,]+[\s]*(per night|/night|a night)',
    r'from[\s]*[\d,]+',
]

ROOM_KEYWORDS = [
    'standard', 'deluxe', 'suite', 'executive', 'superior',
    'double', 'single', 'twin', 'family', 'presidential',
    'junior', 'penthouse', 'studio', 'apartment', 'cottage',
    'lodge', 'villa', 'bungalow', 'chalet'
]

AMENITY_KEYWORDS = [
    'wifi', 'wi-fi', 'internet', 'pool', 'swimming', 'gym',
    'fitness', 'spa', 'restaurant', 'bar', 'parking', 'air conditioning',
    'ac', 'tv', 'television', 'breakfast', 'laundry', 'conference',
    'meeting room', 'airport shuttle', 'generator', 'security'
]

CHECKIN_PATTERNS = [
    r'check[\s-]?in[\s:]+(\d{1,2}(?::\d{2})?[\s]*(?:am|pm)?)',
    r'arrival[\s:]+(\d{1,2}(?::\d{2})?[\s]*(?:am|pm)?)',
]

CHECKOUT_PATTERNS = [
    r'check[\s-]?out[\s:]+(\d{1,2}(?::\d{2})?[\s]*(?:am|pm)?)',
    r'departure[\s:]+(\d{1,2}(?::\d{2})?[\s]*(?:am|pm)?)',
]


# ════════════════════════════════════════════
# SCRAPER FUNCTIONS
# ════════════════════════════════════════════

def fetch_page(url, timeout=15):
    """Fetch a webpage safely with error handling."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'lxml')
    except requests.exceptions.Timeout:
        print(f"  ⚠ Timeout: {url}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"  ⚠ HTTP Error {e.response.status_code}: {url}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"  ⚠ Connection failed: {url}")
        return None
    except Exception as e:
        print(f"  ⚠ Error fetching {url}: {e}")
        return None


def extract_hotel_name(soup, url):
    """Extract hotel name from page."""
    # Try title tag first
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
        # Clean common suffixes
        for suffix in [' | Home', ' - Home', ' | Official', ' - Official Website', ' | Uganda']:
            title = title.replace(suffix, '')
        if title:
            return title.strip()

    # Try h1
    h1 = soup.find('h1')
    if h1:
        return h1.get_text(strip=True)

    # Try og:site_name
    og = soup.find('meta', property='og:site_name')
    if og and og.get('content'):
        return og['content'].strip()

    # Fallback to domain name
    domain = url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
    return domain.split('.')[0].title()


def extract_room_types(soup):
    """Extract room types from page content."""
    found_rooms = []
    text = soup.get_text(' ', strip=True).lower()

    # Find rooms from keywords
    for keyword in ROOM_KEYWORDS:
        if keyword in text:
            # Try to find surrounding context
            idx = text.find(keyword)
            snippet = text[max(0, idx-5):idx+30].strip()
            room_name = snippet.title()
            if room_name not in found_rooms:
                found_rooms.append(room_name)

    # Also check headings and specific elements
    for tag in ['h2', 'h3', 'h4', '.room-title', '.room-type', '.room-name']:
        elements = soup.find_all(tag) if not tag.startswith('.') else soup.select(tag)
        for el in elements:
            text_content = el.get_text(strip=True)
            for kw in ROOM_KEYWORDS:
                if kw in text_content.lower():
                    if text_content not in found_rooms:
                        found_rooms.append(text_content)

    return found_rooms[:8] if found_rooms else ["Not found"]


def extract_prices(soup):
    """Extract pricing information from page."""
    text = soup.get_text(' ', strip=True)
    prices = []

    for pattern in PRICE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        prices.extend(matches)

    # Deduplicate and clean
    unique_prices = list(set(p.strip() for p in prices))
    return unique_prices[:5] if unique_prices else ["Not publicly listed"]


def extract_checkin_checkout(soup):
    """Extract check-in and check-out times."""
    text = soup.get_text(' ', strip=True).lower()
    checkin = "Not found"
    checkout = "Not found"

    for pattern in CHECKIN_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            checkin = match.group(1).strip().upper()
            break

    for pattern in CHECKOUT_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            checkout = match.group(1).strip().upper()
            break

    return checkin, checkout


def extract_amenities(soup):
    """Extract amenities from page."""
    text = soup.get_text(' ', strip=True).lower()
    found = []

    for amenity in AMENITY_KEYWORDS:
        if amenity in text:
            found.append(amenity.title())

    return found if found else ["Not listed"]


def extract_location(soup, url):
    """Extract hotel location/address."""
    # Try address tags
    address = soup.find('address')
    if address:
        return address.get_text(strip=True)

    # Try meta geo tags
    geo = soup.find('meta', {'name': 'geo.placename'})
    if geo and geo.get('content'):
        return geo['content']

    # Search for common address patterns
    text = soup.get_text(' ', strip=True)
    patterns = [
        r'Plot[\s]+\d+[^,\n]+',
        r'\d+[^,\n]+Road[^,\n]*',
        r'P\.?O\.?\s*Box[^,\n]+',
        r'Kampala[^,\n]*',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()

    return "Uganda"


def extract_contact(soup):
    """Extract phone and email."""
    text = soup.get_text(' ', strip=True)

    # Phone
    phone_pattern = r'(\+?256[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{3}|\+?0\d{9}|\d{3}[-\s]\d{3}[-\s]\d{4})'
    phones = re.findall(phone_pattern, text)
    phone = phones[0].strip() if phones else "Not found"

    # Email
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    # Filter out common false positives
    real_emails = [e for e in emails if not any(x in e.lower() for x in ['example', 'youremail', 'email@'])]
    email = real_emails[0] if real_emails else "Not found"

    return phone, email


def extract_description(soup):
    """Extract a brief hotel description."""
    # Try meta description first
    meta_desc = soup.find('meta', {'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        return meta_desc['content'].strip()[:300]

    # Try og:description
    og_desc = soup.find('meta', property='og:description')
    if og_desc and og_desc.get('content'):
        return og_desc['content'].strip()[:300]

    # Try first meaningful paragraph
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if len(text) > 80:
            return text[:300]

    return "No description available"


# ════════════════════════════════════════════
# MAIN SCRAPER
# ════════════════════════════════════════════

def scrape_hotel(url):
    """Scrape all data from a single hotel URL."""
    print(f"\n🔍 Scraping: {url}")

    soup = fetch_page(url)
    if not soup:
        return {
            "hotel_name": url,
            "website": url,
            "room_types": "Failed to fetch",
            "prices": "Failed to fetch",
            "check_in": "N/A",
            "check_out": "N/A",
            "amenities": "Failed to fetch",
            "location": "N/A",
            "phone": "N/A",
            "email": "N/A",
            "description": "Could not access website",
            "status": "FAILED",
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    hotel_name = extract_hotel_name(soup, url)
    room_types = extract_room_types(soup)
    prices = extract_prices(soup)
    checkin, checkout = extract_checkin_checkout(soup)
    amenities = extract_amenities(soup)
    location = extract_location(soup, url)
    phone, email = extract_contact(soup)
    description = extract_description(soup)

    print(f"  ✅ {hotel_name}")
    print(f"     Rooms: {len(room_types)} types found")
    print(f"     Prices: {len(prices)} found")
    print(f"     Amenities: {len(amenities)} found")

    return {
        "hotel_name": hotel_name,
        "website": url,
        "room_types": " | ".join(room_types),
        "prices": " | ".join(prices),
        "check_in": checkin,
        "check_out": checkout,
        "amenities": " | ".join(amenities),
        "location": location,
        "phone": phone,
        "email": email,
        "description": description,
        "status": "SUCCESS",
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def save_csv(data, filename):
    """Save results to CSV."""
    if not data:
        return
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"\n📄 CSV saved: {filename}")


def save_json(data, filename):
    """Save results to JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"📋 JSON saved: {filename}")


def run_scraper(urls, delay=3):
    """
    Main scraper runner.
    delay: seconds between requests (be respectful to servers)
    """
    print("=" * 60)
    print("  TUBAYO HOTEL WEB SCRAPER")
    print("  Extracting hotel data for onboarding")
    print("=" * 60)
    print(f"\n📋 Hotels to scrape: {len(urls)}")

    results = []

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}]", end="")
        data = scrape_hotel(url)
        results.append(data)

        # Respectful delay between requests
        if i < len(urls):
            print(f"  ⏳ Waiting {delay}s before next request...")
            time.sleep(delay)

    # Save outputs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"tubayo_hotels_{timestamp}.csv"
    json_file = f"tubayo_hotels_{timestamp}.json"

    save_csv(results, csv_file)
    save_json(results, json_file)

    # Print summary
    success = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed = sum(1 for r in results if r['status'] == 'FAILED')

    print("\n" + "=" * 60)
    print("  SCRAPING COMPLETE")
    print("=" * 60)
    print(f"  ✅ Successful: {success}")
    print(f"  ❌ Failed:     {failed}")
    print(f"  📁 CSV output: {csv_file}")
    print(f"  📁 JSON output: {json_file}")
    print("=" * 60)

    return results


# ════════════════════════════════════════════
# RUN
# ════════════════════════════════════════════

if __name__ == "__main__":
    results = run_scraper(HOTEL_URLS, delay=3)
