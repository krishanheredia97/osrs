import requests
import tkinter as tk
from tkinter import ttk
import time
import threading
from datetime import datetime, timedelta


class OSRSFlippingCalculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OSRS Active Flipping Calculator")
        self.root.geometry("1200x600")

        self.price_limit = 10_000_000  # 10m gp
        self.min_profit = 10_000  # 10k gp
        self.refresh_interval = 5  # 5 seconds
        self.max_trade_age = 5 * 60  # 5 minutes in seconds

        self.create_widgets()
        self.start_auto_refresh()

    def create_widgets(self):
        refresh_button = ttk.Button(self.root, text="Refresh Now", command=self.refresh_data)
        refresh_button.pack(pady=10)

        columns = ("Item", "Buy Price", "Sell Price", "Margin", "ROI (%)", "Last Buy", "Last Sell")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.status_label = ttk.Label(self.root, text="Status: Ready")
        self.status_label.pack(pady=10)

    def get_latest_prices(self):
        url = "https://prices.runescape.wiki/api/v1/osrs/latest"
        headers = {"User-Agent": "Active Flipping Calculator - TalAslan"}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()['data']
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def calculate_flipping_opportunities(self, data):
        opportunities = []
        current_time = int(time.time())
        for item_id, prices in data.items():
            low_price = prices.get('low')
            high_price = prices.get('high')
            low_time = prices.get('lowTime')
            high_time = prices.get('highTime')

            if all([low_price, high_price, low_time, high_time]) and low_price <= self.price_limit:
                # Check if the item has been traded in the last 5 minutes
                if current_time - low_time <= self.max_trade_age and current_time - high_time <= self.max_trade_age:
                    margin = high_price - low_price - (high_price * 0.01)  # Subtracting 1% of high price
                    if margin >= self.min_profit:
                        roi = (margin / low_price) * 100
                        opportunities.append({
                            'item_id': item_id,
                            'low_price': low_price,
                            'high_price': high_price,
                            'margin': margin,
                            'roi': roi,
                            'low_time': low_time,
                            'high_time': high_time
                        })

        return sorted(opportunities, key=lambda x: x['margin'], reverse=True)[:20]

    def refresh_data(self):
        self.status_label.config(text="Status: Refreshing...")
        self.root.update()

        data = self.get_latest_prices()
        if data:
            opportunities = self.calculate_flipping_opportunities(data)
            self.update_treeview(opportunities)
            self.status_label.config(text=f"Status: Last updated at {time.strftime('%H:%M:%S')}")
        else:
            self.status_label.config(text="Status: Error fetching data")

    def update_treeview(self, opportunities):
        self.tree.delete(*self.tree.get_children())
        for opp in opportunities:
            last_buy_time = datetime.fromtimestamp(opp['low_time']).strftime('%H:%M:%S')
            last_sell_time = datetime.fromtimestamp(opp['high_time']).strftime('%H:%M:%S')
            self.tree.insert("", "end", values=(
                opp['item_id'],
                f"{opp['low_price']:,}",
                f"{opp['high_price']:,}",
                f"{opp['margin']:,.0f}",
                f"{opp['roi']:.2f}%",
                last_buy_time,
                last_sell_time
            ))

    def start_auto_refresh(self):
        def auto_refresh():
            while True:
                self.refresh_data()
                time.sleep(self.refresh_interval)

        thread = threading.Thread(target=auto_refresh, daemon=True)
        thread.start()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = OSRSFlippingCalculator()
    app.run()