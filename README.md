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

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright Browsers**:
   ```bash
   playwright install chromium
   ```

## Usage

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

### Options
- `--url`: Scrape a custom BookMyShow ticket page url.
  ```bash
  python web_scrapper.py --url "https://in.bookmyshow.com/movies/hyderabad/spider-man-brand-new-day/buytickets/ET00502600/20260730"
  ```
