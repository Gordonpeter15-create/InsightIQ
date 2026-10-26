# 📊 InsightIQ

InsightIQ is a Streamlit sales analytics and decision-support app for small supermarkets.
Upload a CSV or Excel sales file and get dashboards, evidence-led business advice, forecasts,
inventory guidance, and downloadable reports.

Recommendations are rule-based and only use what is in the uploaded data. InsightIQ never invents
stock-outs, reorder quantities, suppliers, promotions, customers, or delivery information.

## Features

- **Sign in / create account** – local accounts with PBKDF2-hashed passwords
- **Upload** – CSV or Excel, including formatted workbooks with a title above the header row
- **Currency choice** – pick the currency your sales are recorded in (Home or Settings); it is saved
  to your account and used across every page and the Excel report. Values are labelled, not converted
- **Dashboard** – revenue by product, over time, and by month
- **Ask Your Data** – answers common questions about the uploaded sales
- **Business Advisor** – executive summary (what changed, main risk, best opportunity, next step),
  declining products, and momentum
- **Forecasting** – revenue trend forecast
- **Inventory Guidance** – High Priority / Watch / Opportunity review when stock fields are supplied
- **Reports** – Excel report download

## Data format

Required columns: `Date`, `Product`, `Quantity`, `Price`.

Optional inventory columns (enable Inventory Guidance):

| Field | Accepted column names |
| --- | --- |
| Current stock | `Current Stock`, `Stock Level`, `Stock On Hand` |
| Reorder point | `Reorder Point`, `Minimum Stock`, `Min Stock` |
| Lead time (days) | `Lead Time`, `Lead Time (days)`, `Supplier Lead Days` |

Downloads available in the app:

- `data/InsightIQ_inventory_template.xlsx` – inventory-ready template
- `data/InsightIQ_demo_supermarket.xlsx` – fictional 28-day supermarket dataset for trying every page

## Run locally

Requires Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```

`tests/test_app_smoke.py` renders the home page and every page with the demo dataset,
so run it before each deploy.

## Deploy (Streamlit Community Cloud)

1. Push the repository to GitHub.
2. On share.streamlit.io, create an app from the repo with main file `app.py`.
3. In **Advanced settings**, choose Python 3.11 or newer.

**Account storage limitation:** user accounts are stored in a local SQLite file
(`data/insightiq_users.db`, excluded from git). Streamlit Community Cloud does not keep local files
across restarts or redeploys, so accounts will be lost when the app restarts. For lasting accounts,
deploy to a host with a persistent disk or move accounts to a hosted database.

## Tech stack

Python · Streamlit · pandas · Plotly · openpyxl
