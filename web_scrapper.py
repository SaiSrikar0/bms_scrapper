import sys
import re
import json
import os
import argparse
from datetime import datetime
# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup
# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright
# pyrefly: ignore [missing-import]
from playwright_stealth import Stealth
# pyrefly: ignore [missing-import]
from apscheduler.schedulers.blocking import BlockingScheduler

# Scraper Settings
DEFAULT_URL = "https://in.bookmyshow.com/movies/hyderabad/spider-man-brand-new-day/buytickets/ET00502600/20260730"
SEEN_SLOTS_FILE = "seen_slots.json"

# Keywords for filtering
THEATRE_KEYWORDS = ["prasads", "allu cinemas"]
FORMAT_KEYWORDS = ["3d", "barco", "dolby", "pcx"]

def load_seen_slots():
    """Loads previously seen showtime slots from seen_slots.json."""
    if os.path.exists(SEEN_SLOTS_FILE):
        try:
            with open(SEEN_SLOTS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"[{datetime.now()}] Warning: Failed to load seen slots file: {e}")
    return set()

def save_seen_slots(seen_slots):
    """Saves the current set of seen showtimes to seen_slots.json."""
    try:
        with open(SEEN_SLOTS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen_slots), f, indent=4)
    except Exception as e:
        print(f"[{datetime.now()}] Error saving seen slots: {e}")

def scrape_bms(url=DEFAULT_URL):
    """Scrapes BookMyShow showtimes, filters by keywords, and detects new slots."""
    print(f"\n[{datetime.now()}] Starting BookMyShow scrape execution...")
    
    seen_slots = load_seen_slots()
    new_slots_found = []
    all_current_slots = set()

    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            print(f"[{datetime.now()}] Loading tickets page: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Wait for content rendering/APIs
            page.wait_for_timeout(5000)
            html_content = page.content()
            
            # Extract JSON state
            match = re.search(r"window\.__INITIAL_STATE__\s*=\s*(\{.*\});?", html_content)
            if not match:
                print(f"[{datetime.now()}] Error: Could not find window.__INITIAL_STATE__ in page source.")
                return

            state_data = json.loads(match.group(1))
            showtimes_root = state_data.get("showtimesByEvent", {})
            show_dates_dict = showtimes_root.get("showDates", {})
            
            # Extract date code from URL or find first date key
            # URL format ends in YYYYMMDD, e.g., 20260730
            date_match = re.search(r"/(\d{8})$", url)
            date_code = date_match.group(1) if date_match else None
            
            if not date_code or date_code not in show_dates_dict:
                # Fallback to the first available date key in showDates
                available_dates = list(show_dates_dict.keys())
                if not available_dates:
                    print(f"[{datetime.now()}] Warning: No show dates found in state data.")
                    return
                date_code = available_dates[0]
                print(f"[{datetime.now()}] Using available date code: {date_code}")
            
            day_data = show_dates_dict[date_code]
            venues_dict = day_data.get("primaryStatic", {}).get("data", {}).get("venues", {})
            showtime_widgets = day_data.get("dynamic", {}).get("data", {}).get("showtimeWidgets", [])

            # Locate the groupList widget that houses the venues list
            group_list_widget = None
            for widget in showtime_widgets:
                if widget.get("type") == "groupList":
                    group_list_widget = widget
                    break

            if not group_list_widget:
                print(f"[{datetime.now()}] Error: Could not locate groupList widget in showtime data.")
                return

            venues_list = group_list_widget.get("data", [])[0].get("data", [])

            # Parse showtimes
            for item in venues_list:
                venue_code = item.get("id")
                if not venue_code:
                    continue

                venue_static = venues_dict.get(venue_code, {})
                venue_name = venue_static.get("venueName", "Unknown Venue")
                venue_name_lower = venue_name.lower()

                # Filter: Theatre Match
                is_theatre_match = any(kw in venue_name_lower for kw in THEATRE_KEYWORDS)
                if not is_theatre_match:
                    continue

                showtimes = item.get("showtimes", [])
                matched_shows_info = []

                for show in showtimes:
                    show_time = show.get("showTime") or show.get("title")
                    add_data = show.get("additionalData", {})
                    categories = add_data.get("categories", [])
                    screen_attr = show.get("screenAttr") or add_data.get("attributes") or ""
                    screen_attr_lower = screen_attr.lower()

                    # Collect price categories details
                    price_desc_list = [c.get("priceDesc", "").lower() for c in categories]
                    
                    # Filter: Format Match
                    # Look for keywords in screen attribute or price category descriptions (e.g. 3D in price categories)
                    is_format_match = (
                        any(fmt in screen_attr_lower for fmt in FORMAT_KEYWORDS) or
                        any(any(fmt in desc for desc in price_desc_list) for fmt in FORMAT_KEYWORDS)
                    )
                    
                    if not is_format_match:
                        continue

                    # Construct unique identifier for this slot
                    slot_id = f"{venue_code}_{date_code}_{show_time}_{screen_attr}"
                    all_current_slots.add(slot_id)

                    # Category price formatted string
                    prices = [f"{c.get('priceDesc')}: Rs.{c.get('curPrice')}" for c in categories]
                    show_detail_str = f"Time: {show_time} | Format: {screen_attr} | Prices: [{', '.join(prices)}]"
                    
                    if slot_id not in seen_slots:
                        new_slots_found.append((venue_name, show_detail_str))
                    
                    matched_shows_info.append(show_detail_str)

                # Report matches
                if matched_shows_info:
                    print(f"\n[MATCHED THEATRE] {venue_name} ({venue_code})")
                    for show_info in matched_shows_info:
                        print(f"  - {show_info}")

            # Highlight new slots
            if new_slots_found:
                print(f"\n*** [{datetime.now()}] NEW TIME SLOTS OPENED! ***")
                for venue_name, detail in new_slots_found:
                    print(f"  [{venue_name}] {detail}")
                print("****************************************")
            else:
                print(f"\n[{datetime.now()}] No new time slots detected.")

            # Save the updated seen slots list
            save_seen_slots(all_current_slots)

        except Exception as e:
            print(f"[{datetime.now()}] Scraping exception encountered: {e}")
        finally:
            browser.close()
            print(f"[{datetime.now()}] Scrape execution finished.\n")

def main():
    parser = argparse.ArgumentParser(description="BookMyShow Theatre and Showtime Scraper")
    parser.add_argument("--schedule", action="store_true", help="Run in scheduled mode (every 1 hour)")
    parser.add_argument("--url", type=str, default=DEFAULT_URL, help="Custom BookMyShow tickets URL to scrape")
    args = parser.parse_args()

    if args.schedule:
        print(f"[{datetime.now()}] Starting scheduler to check every 1 hour...")
        scheduler = BlockingScheduler()
        # Run immediately on start
        scrape_bms(args.url)
        # Schedule to run every hour (3600 seconds)
        scheduler.add_job(scrape_bms, 'interval', hours=1, args=[args.url])
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print(f"\n[{datetime.now()}] Scheduler stopped.")
    else:
        scrape_bms(args.url)

if __name__ == "__main__":
    main()
