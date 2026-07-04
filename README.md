# BookMyShow Ticket Scraper & Scheduler

A Python-based BookMyShow scraper that monitors showtimes for specific movies, filters by theater and format preferences, identifies new slots, and runs automatically on an hourly schedule.

## Features
- **Anti-Bot Evading**: Uses `playwright` with `playwright-stealth` context wrapping to bypass security headers and dynamic challenges.
- **Fast & Precise Parsing**: Locates the rendered internal state (`window.__INITIAL_STATE__`) directly from the DOM, guaranteeing highly reliable and structured data processing.
- **Keyword Filtering**:
  - **Theatres**: Filters results for names matching `["prasads", "allu cinemas"]`.
  - **Formats**: Filters results for formats matching `["3d", "barco", "dolby", "pcx"]`.
- **New Slot Alerts**: Stores parsed showtimes in a local database `seen_slots.json` and alerts you when a new time slot opens.
- **Hourly Scheduler**: Can run once or execute periodically every 1 hour via `APScheduler`.
- **Telegram Notifications**: Instantly alerts you on Telegram when a new ticket showtime is opened.

---

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright Browsers**:
   ```bash
   playwright install chromium
   ```

---

## Local Usage

### Run Once
To query showtimes immediately and output the results directly:
```bash
python web_scrapper.py
```

### Run in Scheduled Mode
To run checks immediately and repeat the query **every 1 hour**:
```bash
python web_scrapper.py --schedule
```

### Custom URL Option
- `--url`: Scrape a custom BookMyShow ticket page url.
  ```bash
  python web_scrapper.py --url "https://in.bookmyshow.com/movies/hyderabad/spider-man-brand-new-day/buytickets/ET00502600/20260730"
  ```

---

## Cloud Deployment & Automation (GitHub Actions)

You can automate this script to run **every hour for free** in the cloud using GitHub Actions, ensuring you receive alerts even when your computer is off.

### Step 1: Add GitHub Repository Secrets
For Telegram notifications to work, you must add your Telegram configuration as secrets to your GitHub repository:
1. Go to your repository on GitHub.
2. Select **Settings** > **Secrets and variables** > **Actions**.
3. Click **New repository secret** and add the following two secrets:
   - `TELEGRAM_BOT_TOKEN`: The API token of your Telegram Bot (e.g. `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).
   - `TELEGRAM_CHAT_ID`: Your Telegram Chat ID or group chat ID where the bot should send the messages.

### Step 2: Push changes to GitHub
Once pushed to GitHub, the workflow in `.github/workflows/scrape.yml` will automatically:
- Execute every hour.
- Send a Telegram notification if any new slot opens.
- Commit the updated `seen_slots.json` back to your repo to prevent duplicate alerts.
