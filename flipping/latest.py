import requests
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import pandas as pd


def fetch_5m_data(timestamp=None):
    base_url = "https://prices.runescape.wiki/api/v1/osrs/5m"
    headers = {
        "User-Agent": "OSRS GE API Visualizer - TalAslan"
    }
    params = {}
    if timestamp:
        params['timestamp'] = timestamp

    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
    return None


def process_data(data):
    if not data:
        print("No data received from the API.")
        return None

    print("Received data structure:")
    print(json.dumps(data, indent=2))

    processed_data = []
    timestamp = data.get('timestamp')

    if 'data' not in data:
        print("No 'data' key found in the API response.")
        return None

    for item_id, item_data in data['data'].items():
        processed_entry = {
            'item_id': item_id,
            'timestamp': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp else 'N/A',
            'avg_high_price': item_data.get('avgHighPrice', 'N/A'),
            'avg_low_price': item_data.get('avgLowPrice', 'N/A'),
            'high_price_volume': item_data.get('highPriceVolume', 'N/A'),
            'low_price_volume': item_data.get('lowPriceVolume', 'N/A')
        }
        processed_data.append(processed_entry)

    return pd.DataFrame(processed_data)


class OSRSPriceVisualizer:
    def __init__(self, master):
        self.master = master
        self.master.title("OSRS 5-Minute Price Visualizer")
        self.master.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        # Create a frame for the table
        self.table_frame = ttk.Frame(self.master)
        self.table_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Create the Treeview widget (table)
        self.tree = ttk.Treeview(self.table_frame, columns=(
        "item_id", "timestamp", "avg_high_price", "avg_low_price", "high_price_volume", "low_price_volume"),
                                 show="headings")

        # Define column headings
        self.tree.heading("item_id", text="Item ID")
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("avg_high_price", text="Avg High Price")
        self.tree.heading("avg_low_price", text="Avg Low Price")
        self.tree.heading("high_price_volume", text="High Price Volume")
        self.tree.heading("low_price_volume", text="Low Price Volume")

        # Set column widths
        for col in self.tree["columns"]:
            self.tree.column(col, width=100)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a Refresh button
        refresh_button = ttk.Button(self.master, text="Refresh Data", command=self.refresh_data)
        refresh_button.pack(pady=10)

        # Load initial data
        self.refresh_data()

    def refresh_data(self):
        # Fetch and process data
        result = fetch_5m_data()
        if result:
            df = process_data(result)
            if df is not None and not df.empty:
                # Clear existing data
                for i in self.tree.get_children():
                    self.tree.delete(i)

                # Insert new data
                for index, row in df.iterrows():
                    self.tree.insert("", "end", values=list(row))
            else:
                print("No data to display.")
        else:
            print("Failed to fetch data.")


if __name__ == "__main__":
    root = tk.Tk()
    app = OSRSPriceVisualizer(root)
    root.mainloop()
