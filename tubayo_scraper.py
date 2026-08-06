"""
Tubayo Hotel Web Scraper v2
============================
Upgraded with retry logic, summary report, and config integration.
Scrapes hotel room info from Ugandan hotel websites.
Outputs structured CSV, JSON, and a summary report ready for Tubayo onboarding.

Usage:
    python tubayo_scraper_v2.py

Author: Lincon - Tubayo Operations Lead
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import re
import os
from datetime import datetime, timedelta

# ── IMPORT CONFIG ──
try:
    import config
    USE_CONFIG = True
except ImportError:
    USE_CONFIG = False
    print("⚠️  config.py not found — using default settings")


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

# ── LOAD FROM CONFIG OR USE DEFAULTS ──
if USE_CONFIG:
    DELAY_BETWEEN_REQUESTS = config.DELAY_BETWEEN_REQUESTS
    REQUEST_TIMEOUT = config.REQUEST_TIMEOUT
    MAX_RETRIES = config.MAX_RETRIES
    OUTPUT_FORMAT = config.OUTPUT_FORMAT
    OUTPUT_FOLDER = config.OUTPUT_FOLDER
    HOTEL_URLS = config.HOTEL_URLS
    ROOM_KEYWORDS = config.ROOM_KEYWORDS
    AMENITY_KEYWORDS = config.AMENITY_KEYWORDS
else:
    DELAY_BETWEEN_REQUESTS = 3
    REQUEST_TIMEOUT = 15
    MAX_RETRIES = 2
    OUTPUT_FORMAT = ["csv", "json"]
    OUTPUT_FOLDER = "output"
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
    ROOM_KEYWORDS = [
        'standard', 'deluxe', 'suite', 'executive', 'superior',
        'double', 'single', 'twin', 'family', 'presidential',
        'junior', 'penthouse', 'studio', 'apartment', 'cottage',
        'lodge', 'villa', 'bungalow', 'chalet'
    ]
    AMENITY_KEYWORDS = [
        'wifi', 'wi-fi', 'internet', 'pool', 'swimming', 'gym',
        'fitness', 'spa', 'restaurant', 'bar', 'parking',
        'air conditioning', 'ac', 'tv', 'television', 'breakfast',
        'laundry', 'conference', 'meeting room', 'airport shuttle',
        'generator', 'security', 'rooftop'
    ]

# ── PRICE PATTERNS ──
PRICE_PATTERNS = [
    r'UGX[\s]*[\d,]+',
    r'USD[\s]*[\d,]+',
    r'\$[\d,]+',
    r'[\d,]+[\s]*(per night|/night|a night)',
    r'from[\s]*[\d,]+',
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
# RETRY LOGIC
# ════════════════════════════════════════════

def fetch_page_with_retry(url, timeout=15, max_retries=2):
    """
    Fetch a webpage with exponential backoff retry logic.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds
        max_retries: Number of retry attempts on failure

    Returns:
        tuple: (BeautifulSoup object or None, error message or None)
    """
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser'), None

        except requests.exceptions.Timeout:
            last_error = f"Timeout after {timeout}s"
            if attempt < max_retries:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s...
                print(f"     ⏳ Timeout on attempt {attempt + 1}/{max_retries + 1}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"     ❌ Timeout: All {max_retries + 1} attempts exhausted for {url}")

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            last_error = f"HTTP {status_code}"
            if attempt < max_retries and status_code in [429, 500, 502, 503, 504]:
                wait_time = 2 ** attempt
                print(f"     ⏳ HTTP {status_code} on attempt {attempt + 1}/{max_retries + 1}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"     ❌ HTTP Error {status_code}: {url}")
                break  # Don't retry 4xx client errors (except 429)

        except requests.exceptions.ConnectionError:
            last_error = "Connection failed"
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"     ⏳ Connection failed on attempt {attempt + 1}/{max_retries + 1}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"     ❌ Connection failed: All {max_retries + 1} attempts exhausted for {url}")

        except Exception as e:
            last_error = str(e)
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"     ⏳ Error on attempt {attempt + 1}/{max_retries + 1}: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"     ❌ Error fetching {url}: {e}")

    return None, last_error


def fetch_page(url, timeout=15):
    """Legacy wrapper for backward compatibility."""
    soup, error = fetch_page_with_retry(url, timeout, MAX_RETRIES)
    return soup


# ════════════════════════════════════════════
# SCRAPER FUNCTIONS
# ════════════════════════════════════════════

def extract_hotel_name(soup, url):
    """Extract hotel name from page."""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
        for suffix in [' | Home', ' - Home', ' | Official', ' - Official Website', ' | Uganda']:
            title = title.replace(suffix, '')
        if title:
            return title.strip()

    h1 = soup.find('h1')
    if h1:
        return h1.get_text(strip=True)

    og = soup.find('meta', property='og:site_name')
    if og and og.get('content'):
        return og['content'].strip()

    domain = url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
    return domain.split('.')[0].title()


def extract_room_types(soup):
    """Extract room types from page content."""
    found_rooms = []
    text = soup.get_text(' ', strip=True).lower()

    for keyword in ROOM_KEYWORDS:
        if keyword in text:
            idx = text.find(keyword)
            snippet = text[max(0, idx-5):idx+30].strip()
            room_name = snippet.title()
            if room_name not in found_rooms:
                found_rooms.append(room_name)

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
    address = soup.find('address')
    if address:
        return address.get_text(strip=True)

    geo = soup.find('meta', {'name': 'geo.placename'})
    if geo and geo.get('content'):
        return geo['content']

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

    phone_pattern = r'(\+?256[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{3}|\+?0\d{9}|\d{3}[-\s]\d{3}[-\s]\d{4})'
    phones = re.findall(phone_pattern, text)
    phone = phones[0].strip() if phones else "Not found"

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    real_emails = [e for e in emails if not any(x in e.lower() for x in ['example', 'youremail', 'email@'])]
    email = real_emails[0] if real_emails else "Not found"

    return phone, email


def extract_description(soup):
    """Extract a brief hotel description."""
    meta_desc = soup.find('meta', {'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        return meta_desc['content'].strip()[:300]

    og_desc = soup.find('meta', property='og:description')
    if og_desc and og_desc.get('content'):
        return og_desc['content'].strip()[:300]

    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if len(text) > 80:
            return text[:300]

    return "No description available"


# ════════════════════════════════════════════
# MAIN SCRAPER
# ════════════════════════════════════════════

def scrape_hotel(url):
    """Scrape all data from a single hotel URL with retry logic."""
    print(f"\n🔍 Scraping: {url}")

    soup, error = fetch_page_with_retry(url, timeout=REQUEST_TIMEOUT, max_retries=MAX_RETRIES)

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
            "description": f"Could not access website: {error}",
            "status": "FAILED",
            "error_reason": error,
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
        "error_reason": None,
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def save_csv(data, filename):
    """Save results to CSV."""
    if not data:
        return
    os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"\n📄 CSV saved: {filename}")


def save_json(data, filename):
    """Save results to JSON."""
    os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"📋 JSON saved: {filename}")


# ════════════════════════════════════════════
# SUMMARY REPORT
# ════════════════════════════════════════════

def generate_summary_report(results, start_time, end_time, output_folder):
    """
    Generate a comprehensive summary report of the scraping run.

    Args:
        results: List of hotel data dictionaries
        start_time: When scraping started
        end_time: When scraping finished
        output_folder: Where to save the report

    Returns:
        Dictionary containing the summary data
    """
    total = len(results)
    successful = [r for r in results if r['status'] == 'SUCCESS']
    failed = [r for r in results if r['status'] == 'FAILED']

    # Count fields found across successful scrapes
    fields_found = {
        'hotel_name': sum(1 for r in successful if r.get('hotel_name') and r['hotel_name'] != 'Not found'),
        'room_types': sum(1 for r in successful if r.get('room_types') and r['room_types'] != 'Not found' and r['room_types'] != 'Failed to fetch'),
        'prices': sum(1 for r in successful if r.get('prices') and r['prices'] != 'Not publicly listed' and r['prices'] != 'Failed to fetch'),
        'check_in': sum(1 for r in successful if r.get('check_in') and r['check_in'] != 'Not found'),
        'check_out': sum(1 for r in successful if r.get('check_out') and r['check_out'] != 'Not found'),
        'amenities': sum(1 for r in successful if r.get('amenities') and r['amenities'] != 'Not listed' and r['amenities'] != 'Failed to fetch'),
        'location': sum(1 for r in successful if r.get('location') and r['location'] != 'Uganda' and r['location'] != 'N/A'),
        'phone': sum(1 for r in successful if r.get('phone') and r['phone'] != 'Not found' and r['phone'] != 'N/A'),
        'email': sum(1 for r in successful if r.get('email') and r['email'] != 'Not found' and r['email'] != 'N/A'),
        'description': sum(1 for r in successful if r.get('description') and r['description'] != 'No description available' and r['description'] != 'Could not access website'),
    }

    # Group failures by reason
    failure_reasons = {}
    for r in failed:
        reason = r.get('error_reason', 'Unknown error')
        failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

    duration = end_time - start_time

    summary = {
        "report_generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scraping_session": {
            "started_at": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "finished_at": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": round(duration.total_seconds(), 2),
            "duration_formatted": str(timedelta(seconds=int(duration.total_seconds()))),
        },
        "statistics": {
            "total_hotels": total,
            "successful": len(successful),
            "failed": len(failed),
            "success_rate_percent": round((len(successful) / total * 100), 2) if total > 0 else 0,
        },
        "field_coverage": {
            field: {
                "found": count,
                "out_of": len(successful),
                "coverage_percent": round((count / len(successful) * 100), 2) if successful else 0
            }
            for field, count in fields_found.items()
        },
        "failures": {
            "count": len(failed),
            "by_reason": failure_reasons,
            "failed_hotels": [
                {
                    "url": r['website'],
                    "error_reason": r.get('error_reason', 'Unknown')
                }
                for r in failed
            ]
        },
        "successful_hotels": [
            {
                "name": r['hotel_name'],
                "url": r['website'],
                "rooms_found": len(r['room_types'].split(' | ')) if r.get('room_types') and r['room_types'] != 'Not found' else 0,
                "amenities_found": len(r['amenities'].split(' | ')) if r.get('amenities') and r['amenities'] != 'Not listed' else 0,
            }
            for r in successful
        ]
    }

    # Save summary as JSON
    timestamp = end_time.strftime("%Y%m%d_%H%M%S")
    summary_filename = os.path.join(output_folder, f"tubayo_summary_{timestamp}.json")
    os.makedirs(output_folder, exist_ok=True)

    with open(summary_filename, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Print summary to console
    print("\n" + "=" * 60)
    print("  📊 SCRAPING SUMMARY REPORT")
    print("=" * 60)
    print(f"\n  ⏱️  Duration:        {summary['scraping_session']['duration_formatted']}")
    print(f"  🏨 Total Hotels:    {total}")
    print(f"  ✅ Successful:      {len(successful)}")
    print(f"  ❌ Failed:          {len(failed)}")
    print(f"  📈 Success Rate:    {summary['statistics']['success_rate_percent']}%")
    print("\n  ── Field Coverage ──")
    for field, stats in summary['field_coverage'].items():
        bar = '█' * int(stats['coverage_percent'] / 10) + '░' * (10 - int(stats['coverage_percent'] / 10))
        print(f"  {field:15} {bar} {stats['coverage_percent']}% ({stats['found']}/{stats['out_of']})")

    if failed:
        print("\n  ── Failure Breakdown ──")
        for reason, count in failure_reasons.items():
            print(f"  • {reason}: {count} hotel(s)")
        print("\n  Failed URLs:")
        for r in failed:
            print(f"    ❌ {r['website']} — {r.get('error_reason', 'Unknown')}")

    print(f"\n  📁 Summary saved: {summary_filename}")
    print("=" * 60)

    return summary


# ════════════════════════════════════════════
# MAIN RUNNER
# ════════════════════════════════════════════

def run_scraper(urls=None, delay=None):
    """
    Main scraper runner with retry logic and summary report.

    Args:
        urls: List of hotel URLs (defaults to config.HOTEL_URLS)
        delay: Seconds between requests (defaults to config.DELAY_BETWEEN_REQUESTS)
    """
    urls = urls or HOTEL_URLS
    delay = delay if delay is not None else DELAY_BETWEEN_REQUESTS

    start_time = datetime.now()

    print("=" * 60)
    print("  🏨 TUBAYO HOTEL WEB SCRAPER v2")
    print("  With Retry Logic & Summary Report")
    print("=" * 60)
    print(f"\n📋 Hotels to scrape: {len(urls)}")
    print(f"🔁 Max retries per URL: {MAX_RETRIES}")
    print(f"⏱️  Delay between requests: {delay}s")
    print(f"📁 Output folder: {OUTPUT_FOLDER}")
    print("-" * 60)

    results = []

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}]", end="")
        data = scrape_hotel(url)
        results.append(data)

        if i < len(urls):
            print(f"  ⏳ Waiting {delay}s before next request...")
            time.sleep(delay)

    end_time = datetime.now()

    # Save outputs
    timestamp = end_time.strftime("%Y%m%d_%H%M%S")

    if "csv" in OUTPUT_FORMAT:
        csv_file = os.path.join(OUTPUT_FOLDER, f"tubayo_hotels_{timestamp}.csv")
        save_csv(results, csv_file)

    if "json" in OUTPUT_FORMAT:
        json_file = os.path.join(OUTPUT_FOLDER, f"tubayo_hotels_{timestamp}.json")
        save_json(results, json_file)

    # Generate summary report
    summary = generate_summary_report(results, start_time, end_time, OUTPUT_FOLDER)

    return results, summary


# ════════════════════════════════════════════
# RUN
# ════════════════════════════════════════════

if __name__ == "__main__":
    results, summary = run_scraper()