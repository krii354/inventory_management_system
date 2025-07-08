import pandas as pd
from datetime import datetime
import os

class InventoryManager:
    def __init__(self, file_path, low_stock_threshold=5):
        self.file_path = file_path
        self.low_stock_threshold = low_stock_threshold
        self.load_inventory()

    def load_inventory(self):
        if os.path.exists(self.file_path):
            self.inventory_df = pd.read_excel(self.file_path)
        else:
            self.inventory_df = pd.DataFrame(columns=[
                "Item ID", "Item Name", "Category", "Quantity",
                "Unit Price", "Vendor", "Reorder Level", "Last Updated"
            ])

        expected_cols = ["Item ID", "Item Name", "Category", "Quantity",
                         "Unit Price", "Vendor", "Reorder Level", "Last Updated"]
        for col in expected_cols:
            if col not in self.inventory_df.columns:
                self.inventory_df[col] = ""

        for col in self.inventory_df.columns:
            if self.inventory_df[col].dtype == 'O':
                self.inventory_df[col] = self.inventory_df[col].fillna("")
            else:
                self.inventory_df[col] = self.inventory_df[col].fillna(0)

    def save_inventory(self):
        self.inventory_df.to_excel(self.file_path, index=False)

    def update_inventory(self, items, transaction_type="purchase"):
        for item in items:
            name = item["item"]
            quantity = int(item["quantity"])
            unit_price = float(item["unit_price"])
            category = item.get("category", "Uncategorized")
            vendor = item.get("vendor", "")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 🔍 Match rows with same Item Name and Vendor
            matches = self.inventory_df[
                (self.inventory_df["Item Name"].str.lower() == name.lower()) &
                (self.inventory_df["Vendor"].str.lower() == vendor.lower())
            ]

            # ✅ Case: Found exact match with same price → update
            same_price_match = matches[matches["Unit Price"] == unit_price]

            if not same_price_match.empty:
                idx = same_price_match.index[0]
                if transaction_type == "purchase":
                    self.inventory_df.at[idx, "Quantity"] += quantity
                elif transaction_type == "sale":
                    self.inventory_df.at[idx, "Quantity"] = max(
                        0, self.inventory_df.at[idx, "Quantity"] - quantity
                    )
                self.inventory_df.at[idx, "Last Updated"] = timestamp

            elif transaction_type == "purchase":
                # ✅ No match or different price → add new row
                new_id = self.generate_item_id()
                new_row = {
                    "Item ID": new_id,
                    "Item Name": name,
                    "Category": category,
                    "Quantity": quantity,
                    "Unit Price": unit_price,
                    "Vendor": vendor,
                    "Reorder Level": "",
                    "Last Updated": timestamp
                }
                self.inventory_df = pd.concat([self.inventory_df, pd.DataFrame([new_row])], ignore_index=True)

            elif transaction_type == "sale":
                # ✅ Try to reduce from the latest matching entry (any price)
                if not matches.empty:
                    idx = matches.sort_values(by="Last Updated", ascending=False).index[0]
                    self.inventory_df.at[idx, "Quantity"] = max(
                        0, self.inventory_df.at[idx, "Quantity"] - quantity
                    )
                    self.inventory_df.at[idx, "Last Updated"] = timestamp
                else:
                    # 🛑 Sale of item that doesn't exist
                    print(f"[WARN] Tried to sell unknown item: {name} ({vendor}) — SKIPPED")
                    continue

        self.save_inventory()


    def generate_item_id(self):
        if not self.inventory_df.empty:
            return int(self.inventory_df["Item ID"].max()) + 1
        return 100
