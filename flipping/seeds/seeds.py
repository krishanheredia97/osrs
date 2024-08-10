import requests
import tkinter as tk
from tkinter import ttk
import time

SPELL_COST = 80 / 27
BUY_LIMIT = 200

SEEDS = {
    "Magic": (5316, 5374),
    "Palm": (5289, 5502),
    "Maple": (5314, 5372),
    "Mahogany": (21488, 21480),
    "Yew": (5315, 5373),
    "Papaya": (5288, 5501),
    #"Redwood": (22871, 22859),
    "Celastrus": (22869, 22856),
    #"Dragonfruit": (22877, 22866)
}


def get_item_prices(item_ids):
    url = "https://prices.runescape.wiki/api/v1/osrs/latest"
    headers = {
        "User-Agent": "OSRS GE API Visualizer - TalAslan"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()['data']
        return {item_id: data.get(str(item_id), {}) for item_id in item_ids}
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        return None


def calculate_profit(seed_price, sapling_price, tax_rate=0.01):
    selling_price = sapling_price * (1 - tax_rate)
    return (selling_price - seed_price - SPELL_COST) * BUY_LIMIT


class SeedProfitCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OSRS Seed Profit Calculator")
        self.geometry("1200x600")

        self.create_widgets()

    def create_widgets(self):
        self.refresh_button = ttk.Button(self, text="Refresh Prices", command=self.refresh_prices)
        self.refresh_button.pack(pady=10)

        columns = ("Seed",
                   "Best Buy", "Best Sell", "Best Profit",
                   "Worst Buy", "Worst Sell", "Worst Profit")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("Seed", text="Seed")
        self.tree.heading("Best Buy", text="Best Buy")
        self.tree.heading("Best Sell", text="Best Sell")
        self.tree.heading("Best Profit", text="Best Profit")
        self.tree.heading("Worst Buy", text="Worst Buy")
        self.tree.heading("Worst Sell", text="Worst Sell")
        self.tree.heading("Worst Profit", text="Worst Profit")

        for col in columns:
            self.tree.column(col, width=100, anchor="center")
        self.tree.column("Seed", width=150, anchor="w")

        self.tree.tag_configure("profit", background="#e6ffe6")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.total_label = ttk.Label(self, text="Total Profit: ")
        self.total_label.pack(pady=10)

        self.checkboxes = {}
        for seed in SEEDS:
            var = tk.BooleanVar(value=True)
            self.checkboxes[seed] = var
            self.tree.insert("", tk.END, values=(seed, "", "", "", "", "", ""), tags=(seed,))
            self.tree.tag_bind(seed, "<ButtonRelease-1>", lambda e, s=seed: self.toggle_checkbox(s))

        self.refresh_prices()

    def toggle_checkbox(self, seed):
        current_value = self.checkboxes[seed].get()
        self.checkboxes[seed].set(not current_value)
        self.update_total_profit()

    def refresh_prices(self):
        all_item_ids = [item_id for pair in SEEDS.values() for item_id in pair]
        prices = get_item_prices(all_item_ids)

        if prices:
            profits = []
            for seed, (seed_id, sapling_id) in SEEDS.items():
                seed_data = prices[seed_id]
                sapling_data = prices[sapling_id]

                seed_low = seed_data.get('low')
                seed_high = seed_data.get('high')
                sapling_low = sapling_data.get('low')
                sapling_high = sapling_data.get('high')

                if all([seed_low, seed_high, sapling_low, sapling_high]):
                    best_case = calculate_profit(seed_low, sapling_high)
                    worst_case = calculate_profit(seed_high, sapling_low)
                    profits.append((seed, seed_low, sapling_high, best_case, seed_high, sapling_low, worst_case))

            profits.sort(key=lambda x: x[3], reverse=True)  # Sort by best case profit

            for i, (seed, best_buy, best_sell, best_profit, worst_buy, worst_sell, worst_profit) in enumerate(profits):
                self.tree.item(self.tree.get_children()[i], values=(
                    seed,
                    f"{best_buy:,}", f"{best_sell:,}", f"{best_profit:,.0f}",
                    f"{worst_buy:,}", f"{worst_sell:,}", f"{worst_profit:,.0f}"
                ), tags=(seed, "profit"))

            self.update_total_profit()

    def update_total_profit(self):
        total_best = 0
        total_worst = 0
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            seed = values[0]
            if self.checkboxes[seed].get():
                total_best += float(values[3].replace(",", ""))
                total_worst += float(values[6].replace(",", ""))
        self.total_label.config(text=f"Total Profit: Best Case: {total_best:,.0f} | Worst Case: {total_worst:,.0f}")


if __name__ == "__main__":
    app = SeedProfitCalculator()
    app.mainloop()