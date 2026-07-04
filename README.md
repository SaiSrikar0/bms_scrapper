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
To run checks immediately and repeat the query periodically (e.g., every 10 minutes):
```bash
python web_scrapper.py --schedule --interval 10
```

### Custom URL Option
- `--url`: Scrape a custom BookMyShow ticket page url.
  ```bash
  python web_scrapper.py --url "https://in.bookmyshow.com/movies/hyderabad/spider-man-brand-new-day/buytickets/ET00502600/20260730"
  ```

---

## Cloud Deployment & Automation (GitHub Actions)

### Step 1: Add GitHub Repository Secrets
For Telegram notifications to work, you must add your Telegram configuration as secrets to your GitHub repository:
1. Go to your repository on GitHub.
2. Select **Settings** > **Secrets and variables** > **Actions**.
3. Click **New repository secret** and add the following two secrets:
   - `TELEGRAM_BOT_TOKEN`: The API token of your Telegram Bot (e.g. `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).
   - `TELEGRAM_CHAT_ID`: Your Telegram Chat ID or group chat ID where the bot should send the messages.

### Step 2: Push changes to GitHub
Once pushed to GitHub, the workflow in `.github/workflows/scrape.yml` will automatically support execution.

### Step 3: Set up reliable 10-Minute Cloud Scheduling (Highly Recommended)
GitHub Actions' native scheduler is often delayed by 30-90 minutes. To make it run precisely every 10 minutes, you can trigger it using a free external scheduler like **cron-job.org**:

1. **Create a GitHub Personal Access Token (PAT)**:
   - Go to your GitHub account settings -> **Developer settings** -> **Personal Access Tokens** -> **Tokens (classic)**.
   - Click **Generate new token (classic)**.
   - Give it a name (e.g., `bms-scraper-trigger`), select the **`repo`** (or `public_repo` if public) scope, and generate it.
   - Copy the token immediately.

2. **Configure cron-job.org**:
   - Create a free account at [cron-job.org](https://cron-job.org).
   - Go to **Cronjobs** and click **Create Cronjob**.
   - Set the details:
     - **Title**: `BookMyShow 10m Scraper`
     - **Address (URL)**: `https://api.github.com/repos/SaiSrikar0/bms_scrapper/dispatches`
     - **Request Method**: `POST`
     - **Schedule**: `Every 10 minutes` (User-defined -> custom or pre-set)
   - Under **Headers**, click **Add Header** to add three headers:
     1. Key: `Authorization`, Value: `Bearer <YOUR_GITHUB_PAT>` (replace `<YOUR_GITHUB_PAT>` with your copied token)
     2. Key: `Accept`, Value: `application/vnd.github.v3+json`
     3. Key: `User-Agent`, Value: `cron-job-org`
   - Under **Body**, choose **Raw / JSON** and enter:
     ```json
     {
       "event_type": "trigger_scrape"
     }
     ```
   - Click **Create**. It will now trigger your scraper workflow precisely every 10 minutes!
