# 📦 Inventory Management System

This project is a **web-based Inventory Management System** built using **Flask (Python)**.  
It allows administrators to manage inventory items, process purchases and sales, upload invoices, and maintain a complete audit trail of all inventory-related actions.

This README is **only dedicated to the inventory system** and its functionality.

---

## 🎯 Purpose of the System

The Inventory Management System is designed to:
- Track inventory items accurately
- Handle purchases and sales transactions
- Process invoices and update stock automatically
- Maintain transparency through audit logs and history tracking
- Prevent data inconsistency caused by duplicate items or price variations

---

## 🚀 Key Features

### 🔐 Admin Login
- Secure admin-only access
- Session-based authentication

### 📦 Inventory Operations
- Manual inventory updates (Purchase / Sale)
- Automatic quantity adjustment
- Vendor-wise inventory tracking
- Excel-based persistent storage

### 📄 Invoice Processing
- Upload invoice files (image / text)
- OCR-based text extraction
- Automatic item detection from invoices
- Preview and confirmation before updating inventory

### 🔄 Duplicate Item Handling
- Detect same item & vendor with different prices
- Merge multiple rows into a single consolidated entry

### 🧾 Audit & History Logs
- Audit logs stored in JSON format
- Tracks user, transaction type, timestamp, and item details
- History page for reviewing past inventory actions

---

## 📁 Project Structure

```
.
├── app.py                   # Flask application routes & logic
├── inventory_manager.py     # Inventory update & Excel handling
├── invoice_reader.py        # Invoice OCR and item extraction
├── audit_logger.py          # Audit logging (JSON)
├── utils.py                 # Utility/helper functions
├── config.json              # Configuration file
├── inventory.xlsx           # Inventory data storage
├── audit_log.json           # Inventory audit logs
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── inventory_process.html
│   ├── audit.html
│   └── history.html
│
└── README.md
```

---

## 🛠️ Technologies Used

- Python 3
- Flask
- Pandas
- OpenPyXL
- Pillow (PIL)
- Pytesseract (OCR)
- HTML, Bootstrap 5, Jinja2

---

## ⚙️ Setup & Installation

### 1️⃣ Install Required Packages
```bash
pip install flask pandas pillow pytesseract openpyxl
```

> Ensure **Tesseract OCR** is installed and available in your system PATH.

### 2️⃣ Run the Application
```bash
python app.py
```

Access the system at:
```
http://127.0.0.1:5000/
```

---

## 🔑 Default Admin Credentials

```
Username: admin
Password: admin123
```

---

## 📄 Inventory Data Handling

- Inventory is stored in **inventory.xlsx**
- Each item includes:
  - Item ID
  - Item Name
  - Category
  - Quantity
  - Unit Price
  - Vendor
  - Reorder Level
  - Last Updated

---

## 📊 Audit Logging

Each inventory action records:
- Admin username
- Transaction type (purchase / sale / merge)
- Timestamp
- Item details

Audit logs are stored in **audit_log.json**.

---

## 📌 Intended Use

- Small to medium inventory tracking
- Academic / college inventory system project
- Demonstration of Flask-based inventory applications

---

## ✨ Author

**Adarsh Lakhanpal**  
CSE – Artificial Intelligence & Machine Learning

---

## 📜 Note

This system is focused **only on inventory management** and related operations.
