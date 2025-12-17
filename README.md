# E‑Commerce Sales Dashboard

A small full‑stack sales analytics dashboard for e‑commerce products.  
Users can select a product and see historical monthly sales, yearly totals, and simple forecasts (next 3, 6, 12 months) via a web UI backed by a Flask API.[web:600][web:627]

---

## Live Demo & Code

- **Frontend (Netlify):** https://snazzy-chimera-13fc72.netlify.app  
- **Backend API (Render):** https://e-commerce-sales-dashboard-backend.onrender.com  
- **GitHub repo:** https://github.com/Raven014/E-Commerce-Sales-Dashboard[web:607][web:608]

---

## Features

- Product dropdown populated from `/api/products`.
- Monthly and yearly sales metrics for a selected product.
- Simple future sales forecasts (3/6/12 months) using a lightweight helper.
- CSV download of historical data.
- Light/dark theme toggle and responsive layout.
- Header‑based API key (`X-API-KEY`) and CORS between Netlify and Render.[web:604][web:586]

---

## Tech Stack

- **Frontend:** HTML, CSS, vanilla JavaScript (fetch, DOM, localStorage).[web:627]  
- **Backend:** Python, Flask, Flask‑CORS, SQLite3, pandas.[web:600][web:605][web:606]  
- **Hosting:** Netlify (static frontend) + Render (Flask web service).[web:607][web:608]

---

## API Endpoints

All `/api/*` endpoints expect header:


- `GET /api/products` → list of product names.  
- `POST /api/product-sales` → body `{ "product_name": "<name>" }`, returns product info, monthly sales, yearly total, and forecast data.

---

## Project Structure


E-Commerce-Sales-Dashboard/
├── backend/
│ ├── app.py
│ ├── database.py
│ ├── forecaster.py
│ ├── data/sales.db
│ └── templates/dashboard.html
└── frontend/
├── index.html
├── style.css
└── script.js

## Local Setup (short)

Backend
cd backend
python -m venv venv
venv\Scripts\activate # or source venv/bin/activate
pip install -r requirements.txt
python app.py # runs on http://127.0.0.1:5000


In `frontend/script.js` for local testing:

const API_BASE = 'http://127.0.0.1:5000/api';
const API_KEY = 'raven-secret';


Then open `frontend/index.html` in the browser (or via Live Server).

---

## Notes

- SQLite database is auto‑created and seeded with demo product + sales data on first run.  
- Forecasting is intentionally simple (no heavy ML) to work well on free hosting.
