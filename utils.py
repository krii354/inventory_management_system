# ✅ util.py

import os
from datetime import datetime
import pandas as pd

def ensure_excel_file_exists(file_path):
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=[
            "Item ID", "Item Name", "Category", "Quantity",
            "Unit Price", "Vendor", "Reorder Level", "Last Updated"
        ])
        df.to_excel(file_path, index=False)
        print(f"[INFO] Created new inventory file at {file_path}")
    else:
        print(f"[INFO] Inventory file found: {file_path}")

def log_transaction(items, transaction_type, log_file="transaction_log.txt"):
    with open(log_file, "a") as f:
        f.write(f"\n--- {transaction_type.upper()} on {datetime.now()} ---\n")
        for item in items:
            f.write(f"{item['item']} - Qty: {item['quantity']} - Price: {item['unit_price']}\n")

def log_user_action(username, action, log_file="user_logs.txt"):
    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} | {username} | {action}\n")

