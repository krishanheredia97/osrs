import requests
import json
from datetime import datetime
import pandas as pd

item_id = 565

def fetch_timeseries_data(item_id, timestep="5m"):
    base_url = "https://prices.runescape.wiki/api/v1/osrs"
    endpoint = f"/timeseries?id={item_id}&timestep={timestep}"
    url = base_url + endpoint
    headers = {
        "User-Agent": "Testing OSRS GE API - TalAslan"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
    return None


def process_data(data):
    if not data or 'data' not in data:
        return None

    processed_data = []
    for entry in data['data']:
        processed_entry = {
            'timestamp': datetime.fromtimestamp(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
            'avg_high_price': entry['avgHighPrice'],
            'avg_low_price': entry['avgLowPrice'],
            'high_price_volume': entry['highPriceVolume'],
            'low_price_volume': entry['lowPriceVolume']
        }
        processed_data.append(processed_entry)

    return pd.DataFrame(processed_data)


# Fetch and process data

result = fetch_timeseries_data(item_id)

if result:
    df = process_data(result)
    if df is not None:
        print(df.to_string(index=False))

        # Save to CSV
        csv_filename = f"item_{item_id}_data.csv"
        df.to_csv(csv_filename, index=False)
        print(f"\nData saved to {csv_filename}")
    else:
        print("Failed to process data.")
else:
    print("Failed to fetch data.")
