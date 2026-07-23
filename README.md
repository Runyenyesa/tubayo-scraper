# 🏨 Tubayo Hotel Web Scraper v2

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup4-Scraping-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-v2.0-brightgreen?style=flat-square)

A modular, Python-based web scraping tool that automatically extracts hotel information from Ugandan hotel websites and structures the data into a clean, integration-ready format for the [Tubayo](https://www.tubayo.com) platform — Africa's leading AI-powered travel and marketplace platform.

**v2 now includes:**
- ✅ **Retry Logic** — Exponential backoff automatically retries failed URLs
- ✅ **Summary Report** — Professional end-of-run report with stats, coverage, and failure analysis
- ✅ **Config Integration** — Centralized configuration via `config.py`
- ✅ **Output Folder Support** — Organized output in dedicated folders

---

## 🚀 What It Does

Instead of manually visiting or emailing 400+ hotels for onboarding, this scraper automates the data collection pipeline by extracting key hotel information directly from hotel websites. The output is structured and ready for direct integration into the Tubayo onboarding system.

---

## 📦 Data Fields Extracted

| Field | Description |
|---|---|
| `hotel_name` | Full name of the hotel |
| `website` | Source URL scraped |
| `room_types` | Types of rooms available (Standard, Deluxe, Suite, etc.) |
| `prices` | Room pricing found on the page |
| `check_in` | Check-in time |
| `check_out` | Check-out time |
| `amenities` | Available amenities (WiFi, Pool, Gym, Spa, etc.) |
| `location` | Hotel physical address or location |
| `phone` | Contact phone number |
| `email` | Contact email address |
| `description` | Brief hotel description from meta tags or page content |
| `status` | `SUCCESS` or `FAILED` per hotel |
| `error_reason` | Reason for failure (if failed) |
| `scraped_at` | Timestamp of when the scrape was performed |

---

## 🛠️ Installation

**1. Clone the repository**
```bash
git clone https://github.com/Runyenyesa/tubayo-scraper.git
cd tubayo-scraper
```

**2. Install dependencies**
```bash
pip install requests beautifulsoup4 lxml
```

---

## ▶️ Usage

### Option 1: Use `config.py` (Recommended)

Edit `config.py` to add your target hotel URLs and adjust settings:

```python
HOTEL_URLS = [
    "https://www.yourhotel1.com",
    "https://www.yourhotel2.com",
    # Add as many as needed
]
```

Then run:
```bash
python tubayo_scraper_v2.py
```

### Option 2: Pass URLs directly

```python
from tubayo_scraper_v2 import run_scraper

my_urls = ["https://www.hotel1.com", "https://www.hotel2.com"]
results, summary = run_scraper(urls=my_urls, delay=5)
```

---

## 📁 Output Files

Three files are generated automatically per run in the `output/` folder:

```
output/
├── tubayo_hotels_20260627_143022.csv    # Tabular data for Excel/Sheets
├── tubayo_hotels_20260627_143022.json   # Structured data for API integration
└── tubayo_summary_20260627_143022.json  # Summary report with stats & coverage
```

### Summary Report includes:
- ⏱️ **Duration** — Total time taken for the scraping run
- 📊 **Statistics** — Total, successful, failed, and success rate %
- 📈 **Field Coverage** — Percentage of hotels where each field was found
- ❌ **Failure Breakdown** — Grouped by error reason with URLs
- ✅ **Successful Hotels** — Quick overview of what was found per hotel

---

## ⚙️ Configuration (`config.py`)

| Parameter | Default | Description |
|---|---|---|
| `DELAY_BETWEEN_REQUESTS` | `3` | Wait time between requests — be respectful to servers |
| `REQUEST_TIMEOUT` | `15` | Maximum wait time per page request |
| `MAX_RETRIES` | `2` | Number of retry attempts on failure |
| `OUTPUT_FORMAT` | `["csv", "json"]` | File formats to generate |
| `OUTPUT_FOLDER` | `"output"` | Folder to save all results |
| `HOTEL_URLS` | 13 sample URLs | List of hotel websites to scrape |
| `ROOM_KEYWORDS` | 19 keywords | Words used to detect room types |
| `AMENITY_KEYWORDS` | 23 keywords | Words used to detect amenities |

---

## 🧠 How It Works

```
Hotel URL List (from config.py)
      │
      ▼
  fetch_page_with_retry()   ← Retries with exponential backoff on failure
      │
      ▼
  extract_*()               ← Modular extractors for each field
  ├── hotel_name
  ├── room_types             ← Keyword matching across page content
  ├── prices                 ← Regex patterns for UGX/USD pricing
  ├── checkin/out            ← Time pattern detection
  ├── amenities              ← Keyword list matching
  ├── location               ← Address pattern recognition
  └── contact                ← Phone + email regex extraction
      │
      ▼
  Structured Dict per Hotel
      │
      ▼
  save_csv() + save_json()
      │
      ▼
  generate_summary_report()  ← Professional stats & coverage report
```

---

## 🔁 Retry Logic Details

When a request fails, the scraper automatically retries with **exponential backoff**:

| Attempt | Wait Time | Error Types Retried |
|---|---|---|
| 1st try | 0s (immediate) | Initial attempt |
| 2nd try | 1s | Timeout, Connection Error, HTTP 429/500/502/503/504 |
| 3rd try | 2s | Same as above |
| 4th try | 4s | Same as above |

Client errors (4xx except 429) are **not retried** since they usually indicate a permanent issue.

---

## ⚠️ Error Handling

The scraper handles all failures gracefully:

- **Timeout** — Retried up to `MAX_RETRIES` times, then recorded as `FAILED`
- **HTTP 403/404/500** — Retried if retryable, otherwise recorded with status code
- **Connection error** — Retried with backoff, then recorded as `FAILED`
- **Missing fields** — Recorded as `"Not found"` instead of crashing

No single hotel failure stops the entire scraping run.

---

## 🔮 Roadmap

- [x] Retry logic with exponential backoff
- [x] Summary report with coverage stats
- [x] Config.py integration
- [ ] Selenium upgrade for JavaScript-heavy websites and bot-protected pages
- [ ] Proxy rotation support for large-scale scraping
- [ ] Automatic upload to Tubayo onboarding database via API
- [ ] WhatsApp notification on scrape completion
- [ ] Support for TripAdvisor and Booking.com hotel page parsing
- [ ] Dashboard UI for monitoring scraping progress

---

## 🏗️ Project Structure

```
tubayo-scraper/
│
├── tubayo_scraper.py          # Original scraper (v1)
├── tubayo_scraper_v2.py       # Upgraded scraper (v2) ← NEW
├── config.py                  # Centralized configuration
├── README.md                  # This file
└── output/
    ├── tubayo_hotels_*.csv
    ├── tubayo_hotels_*.json
    └── tubayo_summary_*.json  # NEW: Summary report
```

---

## 👨‍💻 Built By

**Runyenyesa Lincoln**  
Operations Lead — Hotel Onboarding, Tubayo  
Bachelor of Computer Science, Year II  
Mbarara University of Science and Technology (MUST)  
📍 National Innovation Hub, Kampala, Uganda  
🔗 [github.com/Runyenyesa](https://github.com/Runyenyesa)  
🌐 [tubayo.com](https://www.tubayo.com)

---

## 📄 License

This project is licensed under the MIT License — feel free to use, modify and distribute with attribution.

---

> *Built to power the digital onboarding of Uganda's hotel industry onto Africa's leading travel platform.*
