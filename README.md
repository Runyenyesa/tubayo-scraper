# 🏨 Tubayo Hotel Web Scraper

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup4-Scraping-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

A modular, Python-based web scraping tool that automatically extracts hotel information from Ugandan hotel websites and structures the data into a clean, integration-ready format for the [Tubayo](https://www.tubayo.com) platform — Africa's leading AI-powered travel and marketplace platform.

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

**1. Add your target hotel URLs**

Open `tubayo_scraper.py` and update the `HOTEL_URLS` list with the hotel websites you want to scrape:

```python
HOTEL_URLS = [
    "https://www.yourhotel1.com",
    "https://www.yourhotel2.com",
    # Add as many as needed
]
```

**2. Run the scraper**
```bash
python tubayo_scraper.py
```

**3. Collect your output files**

Two files are generated automatically per run:
```
tubayo_hotels_20260627_143022.csv
tubayo_hotels_20260627_143022.json
```

---

## 📁 Output Formats

### CSV (for spreadsheet use)
Clean tabular format ready to open in Excel or Google Sheets for review before uploading to the Tubayo onboarding pipeline.

### JSON (for system integration)
Structured JSON format ready for direct API integration or database import.

**Sample JSON output:**
```json
[
  {
    "hotel_name": "The Emin Pasha Hotel & Spa",
    "website": "https://www.eminpasha.com",
    "room_types": "Standard Room | Deluxe Room | Executive Suite",
    "prices": "USD 120 per night | USD 180 per night",
    "check_in": "2:00 PM",
    "check_out": "11:00 AM",
    "amenities": "WiFi | Pool | Spa | Restaurant | Bar | Gym | Parking",
    "location": "Plot 27 Akii Bua Road, Nakasero, Kampala, Uganda",
    "phone": "+256 414 236 977",
    "email": "gm@eminpasha.com",
    "description": "A boutique luxury hotel in the heart of Kampala.",
    "status": "SUCCESS",
    "scraped_at": "2026-06-27 14:30:22"
  }
]
```

---

## ⚙️ Configuration

| Parameter | Default | Description |
|---|---|---|
| `delay` | `3` seconds | Wait time between requests — be respectful to servers |
| `timeout` | `15` seconds | Maximum wait time per page request |
| `HOTEL_URLS` | 10 sample URLs | List of hotel websites to scrape |

To adjust the delay between requests:
```python
results = run_scraper(HOTEL_URLS, delay=5)  # 5 seconds between requests
```

---

## 🧠 How It Works

```
Hotel URL List
      │
      ▼
  fetch_page()        ← Fetches HTML with browser-like headers
      │
      ▼
  extract_*()         ← Modular extractors for each field
  ├── hotel_name
  ├── room_types       ← Keyword matching across page content
  ├── prices           ← Regex patterns for UGX/USD pricing
  ├── checkin/out      ← Time pattern detection
  ├── amenities        ← Keyword list matching
  ├── location         ← Address pattern recognition
  └── contact          ← Phone + email regex extraction
      │
      ▼
  Structured Dict per Hotel
      │
      ▼
  save_csv() + save_json()
```

---

## ⚠️ Error Handling

The scraper handles all failures gracefully:

- **Timeout** — recorded as `FAILED`, scraper continues to next hotel
- **HTTP 403/404/500** — recorded with status code, scraper continues
- **Connection error** — recorded as `FAILED`, scraper continues
- **Missing fields** — recorded as `"Not found"` instead of crashing

No single hotel failure stops the entire scraping run.

---

## 🔮 Roadmap

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
├── tubayo_scraper.py      # Main scraper script
├── README.md              # This file
└── output/
    ├── tubayo_hotels_*.csv
    └── tubayo_hotels_*.json
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
