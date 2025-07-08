import re
from PIL import Image
import pytesseract

class InvoiceReader:
    def read_text_from_image(self, image_path):
        img = Image.open(image_path)
        return pytesseract.image_to_string(img)

    def read_invoice_file(self, filepath):
        if filepath.lower().endswith((".png", ".jpg", ".jpeg", ".pdf")):
            return self.read_text_from_image(filepath)
        else:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()

    def extract_items(self, text):
        # Step 1: Find the "- Items:" section
        if "- Items:" not in text:
            return []

        items_section = text.split("- Items:")[-1].strip()
        lines = items_section.splitlines()

        items = []
        for line in lines:
            # Only process lines that look like: (item, qty, price, cat, vendor)
            match = re.match(r'\((.*?),\s*(\d+),\s*([\d.]+),\s*(.*?),\s*(.*?)\)', line.strip())
            if match:
                item, qty, price, category, vendor = match.groups()
                items.append({
                    "item": item.strip(),
                    "quantity": int(qty),
                    "unit_price": float(price),
                    "category": category.strip(),
                    "vendor": vendor.strip()
                })

        return items
