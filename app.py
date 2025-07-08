# ✅ FULL UPDATED app.py

import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session
from inventory_manager import InventoryManager
from invoice_reader import InvoiceReader
from audit_logger import AuditLogger
from utils import ensure_excel_file_exists, log_transaction, log_user_action
from functools import wraps
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "my_super_secret_key")

with open("config.json", "r") as f:
    config = json.load(f)

inventory_path = config["inventory_file"]
low_stock_threshold = config.get("low_stock_threshold", 5)
ensure_excel_file_exists(inventory_path)

manager = InventoryManager(inventory_path, low_stock_threshold)
reader = InvoiceReader()
audit_logger = AuditLogger()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash("Please login to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def home():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "admin123":
            session['username'] = username
            flash("Login successful", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully", "info")
    return redirect(url_for("login"))

@app.route("/inventory")
@login_required
def inventory():
    return redirect(url_for("inventory_view"))

@app.route("/inventory_view")
@login_required
def inventory_view():
    vendor_filter = request.args.get("vendor")
    df = manager.inventory_df.copy()

    if vendor_filter and vendor_filter != "All":
        df = df[df["Vendor"].str.lower() == vendor_filter.lower()]

    # Detect duplicates (same item & vendor, diff prices)
    dup_groups = df.groupby(["Item Name", "Vendor"])["Unit Price"].nunique()
    duplicate_keys = set(dup_groups[dup_groups > 1].index)

    # Add 'is_duplicate' column to flag rows
    df["is_duplicate"] = df.apply(
        lambda row: (row["Item Name"], row["Vendor"]) in duplicate_keys,
        axis=1
    )

    vendors = sorted(set(manager.inventory_df["Vendor"].dropna().unique()))
    return render_template(
        "inventory_view.html",
        inventory=df.to_dict(orient="records"),
        vendors=vendors,
        selected_vendor=vendor_filter or "All"
    )



@app.route("/process", methods=["GET", "POST"])
@login_required
def process_invoice():
    if request.method == "POST":
        if "manual_submit" in request.form:
            item = request.form.get("item")
            qty_str = request.form.get("quantity")
            price_str = request.form.get("unit_price")
            category = request.form.get("category") or "Uncategorized"
            vendor = request.form.get("vendor") or ""
            txn_type = request.form.get("transaction_type") or "unknown"

            try:
                if qty_str is None or price_str is None:
                    raise ValueError("Quantity or price is missing.")
                quantity = int(qty_str)
                price = float(price_str)
            except (ValueError, TypeError):
                flash("Invalid quantity or price.", "error")
                return redirect(url_for("process_invoice"))

            item_data = [{
                "item": item,
                "quantity": quantity,
                "unit_price": price,
                "category": category,
                "vendor": vendor
            }]

            manager.update_inventory(item_data, transaction_type=txn_type)
            audit_logger.log(session.get("username", "unknown"), txn_type, item_data)
            flash(f"Inventory updated: {txn_type} of {quantity} {item}(s)", "success")
            return redirect(url_for("process_invoice"))

        elif "preview_invoice" in request.form:
            if 'invoice_file' not in request.files:
                flash("Invoice file missing.", "error")
                return redirect(request.url)

            file = request.files['invoice_file']
            if not file.filename:
                flash("No file selected.", "error")
                return redirect(request.url)

            os.makedirs("uploads", exist_ok=True)
            filename = file.filename or "uploaded_invoice"
            filepath = os.path.join("uploads", filename)
            file.save(filepath)

            # 🔁 Read + extract invoice items
            invoice_text = reader.read_invoice_file(filepath)
            extracted_items = reader.extract_items(invoice_text)
            print(f"Extracted items: {extracted_items}")

            if not extracted_items:
                flash("No items found in the invoice.", "error")
                return redirect(request.url)    
            # 🔍 Check if items exist in inventory
            inventory_items = [iname.lower() for iname in manager.inventory_df["Item Name"].tolist()]
            for item in extracted_items:
                item["status"] = "existing" if item["item"].lower() in inventory_items else "new"

            # ✅ Finally render page with data
            return render_template("inventory_process.html", extracted_items=extracted_items)

    return render_template("inventory_process.html", extracted_items=None)

@app.route("/confirm_invoice_update", methods=["POST"])
@login_required
def confirm_invoice_update():
    txn_type = request.form.get("transaction_type") or "unknown"
    items_json = request.form.get("items_json")

    if not items_json:
        flash("No items data provided.", "error")
        return redirect(url_for("inventory_view"))

    try:
        items = json.loads(items_json)
    except json.JSONDecodeError:
        flash("Invalid item data.", "error")
        return redirect(url_for("inventory_view"))

    manager.update_inventory(items, transaction_type=txn_type)
    audit_logger.log(session.get("username", "unknown"), txn_type, items)
    log_transaction(items, txn_type)
    flash("Inventory updated successfully from invoice.", "success")
    return redirect(url_for("inventory_view"))

@app.route("/audit")
@login_required
def audit_logs():
    return render_template("audit.html", logs=audit_logger.get_logs())

@app.route("/history")
@login_required
def history():
    return render_template("history.html", logs=audit_logger.get_logs())


@app.route("/merge_item", methods=["POST"])
@login_required
def merge_item():
    item_name = request.form.get("item")
    vendor = request.form.get("vendor")
    new_price = request.form.get("new_price")

    if not item_name or not vendor or new_price is None:
        flash("Invalid merge request: missing item/vendor/price.", "error")
        return redirect(url_for("inventory_view"))

    try:
        new_price = float(new_price)
    except (ValueError, TypeError):
        flash("Invalid new price entered.", "error")
        return redirect(url_for("inventory_view"))

    df = manager.inventory_df
    matching = df[
        (df["Item Name"].str.lower() == item_name.lower()) &
        (df["Vendor"].str.lower() == vendor.lower())
    ]

    if matching.empty:
        flash("No matching items found to merge.", "error")
        return redirect(url_for("inventory_view"))

    total_qty = matching["Quantity"].sum()
    category = matching["Category"].mode()[0] if not matching["Category"].mode().empty else "Uncategorized"
    reorder = matching["Reorder Level"].mode()[0] if not matching["Reorder Level"].mode().empty else ""

    # Remove old entries
    manager.inventory_df = df[~(
        (df["Item Name"].str.lower() == item_name.lower()) &
        (df["Vendor"].str.lower() == vendor.lower())
    )]

    # Add merged entry
    merged_item = {
        "Item ID": manager.generate_item_id(),
        "Item Name": item_name,
        "Category": category,
        "Quantity": total_qty,
        "Unit Price": new_price,
        "Vendor": vendor,
        "Reorder Level": reorder,
        "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    manager.inventory_df = pd.concat(
        [manager.inventory_df, pd.DataFrame([merged_item])],
        ignore_index=True
    )
    manager.save_inventory()

    # ✅ Log this merge to audit log
    audit_logger.log(
        user=session.get("username", "unknown"),
        transaction_type="merge",
        items=[merged_item]
    )

    flash(f"Merged {len(matching)} rows for '{item_name}' from vendor '{vendor}' at ₹{new_price}.", "success")
    return redirect(url_for("inventory_view"))




if __name__ == "__main__":
    app.run(debug=True)
