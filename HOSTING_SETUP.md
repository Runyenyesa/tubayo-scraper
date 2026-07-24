# 🚀 Free Hosting Setup Guide — Tubayo Hotel Scraper

This guide walks you through hosting the Tubayo Hotel Scraper **completely for free** using GitHub's built-in services.

---

## 📋 What You'll Get (All Free)

| Feature | Service | Cost |
|---------|---------|------|
| 🤖 Automated scraping | GitHub Actions | **$0** (public repo = unlimited) |
| 📊 Results dashboard | GitHub Pages | **$0** (public repo = free) |
| 💾 Data storage | GitHub Repository | **$0** (public repo = free) |
| ⏰ Scheduled runs | GitHub Actions Cron | **$0** |
| ▶️ Manual triggers | GitHub UI | **$0** |

---

## 🛠️ Step-by-Step Setup

### Step 1: Make Your Repo Public

Your repo **must be public** for free GitHub Actions and Pages.

1. Go to your repo: `https://github.com/Runyenyesa/article-speed-reader`
2. Click **Settings** → scroll to **Danger Zone**
3. Click **Change visibility** → **Make public**
4. Confirm with your password

> ⚠️ **Why public?** GitHub Actions and Pages are 100% free for public repos. Private repos cost money.

---

### Step 2: Add the New Files to Your Repo

Copy these files into your repository (replace existing ones where needed):

```
article-speed-reader/
├── .github/
│   └── workflows/
│       └── scraper.yml          ← NEW: GitHub Actions workflow
├── docs/
│   └── index.html               ← NEW: Dashboard website
├── output/                      ← NEW: Folder for scrape results
├── tubayo_scraper_v2.py         ← NEW: Upgraded scraper
├── config.py                    ← EXISTING: Your config
└── README.md                    ← UPDATE: Use README_v2.md
```

**Option A: Upload via GitHub web UI**
1. Go to your repo on GitHub
2. Click **Add file** → **Upload files**
3. Drag and drop the files/folders
4. Commit with message: `feat: Add v2 scraper with hosting setup`

**Option B: Command line**
```bash
# Clone your repo
git clone https://github.com/Runyenyesa/article-speed-reader.git
cd article-speed-reader

# Copy the new files (adjust paths as needed)
cp /path/to/tubayo_scraper_v2.py .
cp /path/to/config.py .
mkdir -p .github/workflows
cp /path/to/scraper.yml .github/workflows/
mkdir -p docs
cp /path/to/index.html docs/
mkdir -p output

# Commit and push
git add .
git commit -m "feat: Add v2 scraper with GitHub Actions + Pages hosting

- Add retry logic and summary report
- Add GitHub Actions workflow for automated scraping
- Add GitHub Pages dashboard for viewing results
- Integrate config.py for centralized settings"
git push origin main
```

---

### Step 3: Enable GitHub Pages

1. Go to **Settings** → **Pages** (in the left sidebar)
2. Under **Build and deployment**:
   - **Source**: Select **Deploy from a branch**
   - **Branch**: Select `main` / `docs` folder
   - Click **Save**
3. Wait 1-2 minutes for the site to deploy
4. Your dashboard will be at:
   ```
   https://runyenyesa.github.io/article-speed-reader
   ```

---

### Step 4: Verify GitHub Actions Workflow

1. Go to **Actions** tab in your repo
2. You should see the **🏨 Tubayo Hotel Scraper** workflow
3. Click on it → **Run workflow** → **Run workflow** (green button)
4. This will trigger your first scrape!

---

### Step 5: Set Up Daily Auto-Scraping

The workflow is already configured to run **daily at 6:00 AM UTC**.

To change the schedule, edit `.github/workflows/scraper.yml`:

```yaml
schedule:
  - cron: '0 6 * * *'    # Daily at 6 AM UTC
  - cron: '0 */6 * * *'  # Every 6 hours
  - cron: '0 0 * * 0'    # Weekly on Sunday
```

**Cron format:** `minute hour day month day-of-week`

| Schedule | Cron |
|----------|------|
| Every hour | `0 * * * *` |
| Every 6 hours | `0 */6 * * *` |
| Daily at 6 AM | `0 6 * * *` |
| Weekly (Sunday) | `0 0 * * 0` |
| Monthly (1st) | `0 0 1 * *` |

---

## 🎯 How to Use

### Run Scraper Manually
1. Go to **Actions** → **🏨 Tubayo Hotel Scraper**
2. Click **Run workflow** (dropdown on the right)
3. (Optional) Enter custom URLs or leave blank for config.py defaults
4. Click **Run workflow**
5. Watch the live logs!

### View Results
- **Dashboard**: `https://runyenyesa.github.io/article-speed-reader`
- **Raw files**: Browse the `output/` folder in your repo
- **Latest CSV/JSON**: Check the `output/` folder on GitHub

### Download Results
1. Go to your repo → `output/` folder
2. Click on any `.csv` or `.json` file
3. Click **Raw** → Right-click → **Save as**

---

## 📁 Output Files Explained

After each run, these files appear in `output/`:

| File | Purpose |
|------|---------|
| `tubayo_hotels_YYYYMMDD_HHMMSS.csv` | Spreadsheet for Excel/Google Sheets |
| `tubayo_hotels_YYYYMMDD_HHMMSS.json` | Structured data for API integration |
| `tubayo_summary_YYYYMMDD_HHMMSS.json` | Stats, coverage, failure analysis |

---

## 🔧 Troubleshooting

### "Workflow not running"
- Make sure the repo is **public**
- Check **Actions** → **Permissions** → Allow all actions

### "No output files"
- The scraper needs to complete successfully first
- Check the Actions log for errors
- Some hotel sites may block scraping (that's what retry logic is for!)

### "Dashboard shows 'No scrape data yet'"
- Run the scraper at least once
- The dashboard reads from `output/` folder
- Wait 1-2 minutes after scrape completes for files to commit

### "Pages site not loading"
- Go to **Settings** → **Pages** and verify source is `main` / `docs`
- It can take up to 10 minutes to deploy
- URL format: `https://USERNAME.github.io/REPO-NAME`

---

## 🎓 Pro Tips

1. **Add more hotels**: Edit `config.py` → add URLs to `HOTEL_URLS`
2. **Adjust retry settings**: Edit `config.py` → change `MAX_RETRIES`, `DELAY_BETWEEN_REQUESTS`
3. **Get notifications**: GitHub can email you when Actions fail (Settings → Notifications)
4. **Keep history**: Old scrape files stay in `output/` — great for tracking changes over time

---

## 💰 Cost Breakdown

| Component | Free Tier | Your Usage | Cost |
|-----------|-----------|------------|------|
| GitHub Actions (public repo) | Unlimited | ~30 min/run | **$0** |
| GitHub Pages | Unlimited | ~1 MB site | **$0** |
| GitHub Storage | Unlimited (public) | ~10 MB data | **$0** |
| **TOTAL** | | | **$0** |

---

## 🚀 Next Steps

Once this is running, we can add:
- [ ] **Selenium support** — for JavaScript-heavy hotel sites
- [ ] **Progress bar** — live progress in GitHub Actions logs
- [ ] **Email/Slack notifications** — when scraping completes
- [ ] **WhatsApp alerts** — ping you on completion
- [ ] **Database integration** — auto-upload to Tubayo API

---

Built with ❤️ for Tubayo | Runyenyesa Lincoln
