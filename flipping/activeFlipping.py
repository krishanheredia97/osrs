import requests
import json
from flask import Flask, render_template, send_from_directory
import time
from datetime import datetime
import os

app = Flask(__name__)

class OSRSFlippingCalculator:
    def __init__(self):
        self.price_limit = 10_000_000  # 10m gp
        self.min_profit = 10_000  # 10k gp
        self.refresh_interval = 5  # 5 seconds
        self.max_trade_age = 5 * 60  # 5 minutes in seconds
        self.items_data = self.load_items_data()

    def load_items_data(self):
        with open('items.json', 'r') as f:
            items_list = json.load(f)
        return {str(item['id']): item for item in items_list}

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
                if current_time - low_time <= self.max_trade_age and current_time - high_time <= self.max_trade_age:
                    margin = high_price - low_price - (high_price * 0.01)  # Subtracting 1% of high price
                    if margin >= self.min_profit:
                        roi = (margin / low_price) * 100
                        item_name = self.get_item_name(item_id)
                        icon_path = self.get_item_icon(item_id)
                        opportunities.append({
                            'item_id': item_id,
                            'name': item_name,
                            'icon': icon_path,
                            'low_price': low_price,
                            'high_price': high_price,
                            'margin': margin,
                            'roi': roi,
                            'low_time': self.format_time_ago(current_time - low_time),
                            'high_time': self.format_time_ago(current_time - high_time)
                        })

        return sorted(opportunities, key=lambda x: x['margin'], reverse=True)[:20]

    def get_item_name(self, item_id):
        item_data = self.items_data.get(str(item_id))
        return item_data['name'] if item_data else f"Unknown Item ({item_id})"

    def get_item_icon(self, item_id):
        icon_path = f"icons/{item_id}.png"
        if os.path.exists(icon_path):
            return icon_path
        return "icons/default.png"  # Assuming you have a default icon

    def format_time_ago(self, seconds):
        if seconds < 60:
            return f"{seconds}s ago"
        elif seconds < 3600:
            return f"{seconds // 60}m ago"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}:{minutes:02d}h ago"
        else:
            return f"{seconds // 86400}d ago"

calculator = OSRSFlippingCalculator()

@app.route('/')
def index():
    data = calculator.get_latest_prices()
    if data:
        opportunities = calculator.calculate_flipping_opportunities(data)
        return render_template('index.html', opportunities=opportunities)
    else:
        return "Error fetching data", 500

@app.route('/icons/<path:filename>')
def serve_icon(filename):
    return send_from_directory('icons', filename)

if __name__ == "__main__":
    app.run(debug=True)