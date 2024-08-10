import json
import requests
import os
import time
import random
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(filename='icon_download.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Constants
ICONS_DIR = '../flipping/icons'
ITEMS_JSON = 'items.json'
USER_AGENT = 'OSRS Icon Downloader Bot for Flipping Website (contact: info@krishanheredia.com)'

def load_items():
    with open(ITEMS_JSON, 'r') as f:
        return json.load(f)

def download_icon(item, session):
    icon_path = os.path.join(ICONS_DIR, f"{item['id']}.png")

    if os.path.exists(icon_path):
        print(f"Skipping existing icon for item {item['id']}")
        logging.info(f"Skipping existing icon for item {item['id']}")
        return

    try:
        response = session.get(item['link'], stream=True)
        response.raise_for_status()

        with open(icon_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
            f.flush()
            os.fsync(f.fileno())

        print(f"Downloaded and saved icon for item {item['id']}")
        logging.info(f"Downloaded and saved icon for item {item['id']}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download icon for item {item['id']}: {str(e)}")
        logging.error(f"Failed to download icon for item {item['id']}: {str(e)}")

def exponential_backoff(attempt, base_delay=5, max_delay=300):
    delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
    return delay

def main():
    if not os.path.exists(ICONS_DIR):
        os.makedirs(ICONS_DIR)

    items = load_items()
    total_items = len(items)

    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})

    for i, item in enumerate(items, 1):
        attempt = 0
        while True:
            try:
                download_icon(item, session)
                break
            except requests.exceptions.RequestException as e:
                attempt += 1
                delay = exponential_backoff(attempt)
                print(f"Request failed for item {item['id']}. Retrying in {delay:.2f} seconds. Error: {str(e)}")
                logging.warning(f"Request failed for item {item['id']}. Retrying in {delay:.2f} seconds. Error: {str(e)}")
                time.sleep(delay)
                if attempt > 5:
                    print(f"Failed to download icon for item {item['id']} after 5 attempts. Moving on.")
                    logging.error(f"Failed to download icon for item {item['id']} after 5 attempts. Moving on.")
                    break

        if i % 10 == 0:
            print(f"Progress: {i}/{total_items}")
            logging.info(f"Progress: {i}/{total_items}")

        time.sleep(random.uniform(1, 3))  # Random delay between 1 and 3 seconds

if __name__ == "__main__":
    start_time = datetime.now()
    print(f"Starting icon download at {start_time}")
    logging.info(f"Starting icon download at {start_time}")
    main()
    end_time = datetime.now()
    print(f"Completed icon download at {end_time}")
    print(f"Total time: {end_time - start_time}")
    logging.info(f"Completed icon download at {end_time}")
    logging.info(f"Total time: {end_time - start_time}")
