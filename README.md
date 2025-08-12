# Bynry Inventory Management - Backend Intern Solution

This repository contains my complete solution for the Backend Engineering Intern case study.

## 📂 Repository Contents

* **solution.md** - Written answers for all three parts:

  * Code Review & Debugging
  * Database Design
  * API Implementation
* **app.py** - Minimal Flask + SQLAlchemy application with:

  * Corrected `create_product` API
  * Low Stock Alerts API
* **schema.sql** - SQL schema for the database (PostgreSQL syntax, can be adapted to MySQL/SQLite)
* **README.md** - Documentation and setup instructions

---

## 🚀 Setup Instructions

### 1. Clone this repository

```bash
git clone https://github.com/Ashex360/bynry-inventory-bd-intern-solution.git
cd bynry-inventory-bd-intern-solution
```

### 2. Install dependencies

Make sure you have **Python 3.8+** installed.

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install flask flask_sqlalchemy psycopg2-binary
```

### 3. Create and set up the database

Update the database URL in `app.py` if needed (default uses SQLite).

```bash
# For PostgreSQL:
createdb bynry_db
psql -d bynry_db -f schema.sql
```

### 4. Run the application

```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/bynry_db
python app.py
```

The app will run on **[http://127.0.0.1:5000](http://127.0.0.1:5000)**.

---

## 📌 Example API Endpoints

### Create Product

**POST** `/api/products`

```json
{
  "name": "Widget A",
  "sku": "WID-001",
  "price": 25.50,
  "warehouse_id": 1,
  "initial_quantity": 100
}
```

### Low Stock Alerts

**GET** `/api/companies/1/alerts/low-stock`

---

## 📝 Notes

* Database schema is kept minimal for clarity but supports all listed requirements.
* The solution focuses on correctness, clarity, and meeting assignment requirements within time constraints.
* Business logic assumptions and missing requirements are documented in `solution.md`.
