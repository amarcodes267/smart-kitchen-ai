# AI Kitchen

AI Kitchen is a Flask-based kitchen operations platform for managing kitchens, menus, inventory, sales, food waste, demand predictions, and preparation recommendations.

The project includes:

- A server-rendered web interface built with Flask templates.
- REST endpoints for kitchen operations.
- SQLite support for local development and PostgreSQL support through `DATABASE_URL`.
- An XGBoost demand-prediction training pipeline.
- Inventory-aware and waste-aware preparation recommendations.
- Automated API and end-to-end tests.

## Project status

The application is suitable for local development and demonstration. Before production use, configure a managed database, replace demonstration data with validated business data, secure all secrets, and run the deployment hardening steps described below.

## Requirements

- Python 3.10 or newer
- `pip`
- Git
- PostgreSQL (optional; SQLite is used by default for local development)

Python dependencies are listed in `requirements.txt` when that file is present in the project distribution. Install them with:

```powershell
python -m pip install -r requirements.txt
```

## Installation

From the `AI-KITCHEN` directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## Configuration

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Set values appropriate for the environment:

| Variable | Description |
| --- | --- |
| `SECRET_KEY` | Secret used by Flask. Use a long random value outside development. |
| `DATABASE_URL` | SQLAlchemy database URL. Example: `sqlite:///smart_kitchen.db`. |
| `GEMINI_API_KEY` | Optional Gemini API key for AI text generation. |
| `FLASK_DEBUG` | Set to `True` only for local development. |

Never commit `.env`, real API keys, database passwords, or other credentials. Use deployment-platform secrets or an external secret manager in production.

## Running the application

Start the development server:

```powershell
python app.py
```

The application listens on `http://127.0.0.1:5000`.

Useful pages:

- `/` — landing page
- `/dashboard` — operational dashboard
- `/kitchen-setup` — kitchen setup
- `/menu` — menu management
- `/inventory` — inventory management
- `/sales` — sales records
- `/waste` — waste records and analysis
- `/predictions` — demand prediction
- `/recommendations` — preparation recommendations
- `/health` — health check

Example health check:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/health
```

The app creates local database tables on startup. For production, use a migration system before deploying schema changes.

## Machine-learning pipeline

### Dataset format

Place the training CSV at:

```text
data/raw/kitchen_data.csv
```

The training pipeline expects these columns:

```text
week
center_id
meal_id
checkout_price
base_price
emailer_for_promotion
homepage_featured
num_orders
```

`num_orders` is the prediction target. Numeric values are cleaned and missing numeric values are handled by `ml/preprocessing.py`.

### Train a model

Run from the project directory:

```powershell
python ml/train.py
```

The trained artifact is saved to:

```text
ml/model.pkl
```

The training command prints the record count, feature list, test-set mean absolute error, and output path. Always evaluate model quality using a representative holdout dataset before production use.

### Make a prediction

The prediction API accepts:

```json
{
  "week": 1,
  "center_id": 55,
  "meal_id": 1885,
  "checkout_price": 158.11,
  "base_price": 159.11,
  "emailer_for_promotion": 0,
  "homepage_featured": 0
}
```

Example request:

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:5000/api/prediction/ `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"week":1,"center_id":55,"meal_id":1885,"checkout_price":158.11,"base_price":159.11,"emailer_for_promotion":0,"homepage_featured":0}'
```

## API overview

| Area | Base endpoint | Main operations |
| --- | --- | --- |
| Kitchens | `/api/kitchen/` | Create and list kitchens |
| Menus | `/api/menu/` | Add, list, and delete menu items |
| Inventory | `/api/inventory/` | Add, list, update, and delete stock |
| Sales | `/api/sales/` | Record and retrieve sales |
| Waste | `/api/waste/` | Record waste, summaries, and high-waste items |
| Predictions | `/api/prediction/` | Predict demand |
| Recommendations | `/api/recommendation/` | Recommend preparation quantities |
| Data | `/api/data/` | Data import and related operations |
| Preparation | `/api/preparation/` | Preparation planning operations |

Successful responses generally contain `"success": true`. Validation failures return a JSON message and an HTTP 4xx status. Server failures return a 5xx status.

## Testing

Run the full test suite:

```powershell
python -m pytest -q
```

Run end-to-end tests only:

```powershell
python -m pytest tests/test_e2e.py -q
```

The tests use the configured database connection. Use a dedicated test database or SQLite configuration so test data cannot affect operational data.

## Project structure

```text
AI-KITCHEN/
├── app.py                    # Flask application and page routes
├── backend/
│   ├── models/               # SQLAlchemy models
│   ├── routes/               # REST API blueprints
│   ├── services/             # Prediction, waste, optimization, and AI services
│   └── utils/                # Configuration and database helpers
├── data/
│   ├── raw/                  # Input training data
│   └── processed/            # Generated feature data
├── ml/
│   ├── preprocessing.py      # Data cleaning and feature engineering
│   ├── train.py              # Model training and evaluation
│   └── predict.py            # Prediction utilities
├── static/                   # CSS and JavaScript assets
├── templates/                # HTML templates
├── tests/                    # Unit, API, and end-to-end tests
└── notebooks/                # Exploratory notebooks
```

## Production checklist

Before deployment:

1. Replace demonstration or synthetic data with verified historical data.
2. Retrain and evaluate the model using a time-aware validation strategy.
3. Pin dependency versions and scan dependencies for known vulnerabilities.
4. Use PostgreSQL or another managed database.
5. Add database migrations and run migrations during deployment.
6. Set a strong `SECRET_KEY` and keep all credentials outside source control.
7. Set `FLASK_DEBUG=False`.
8. Run behind a production WSGI server such as Gunicorn.
9. Add authentication and authorization for API endpoints.
10. Configure structured logs, backups, monitoring, and error reporting.
11. Add request limits and input validation for public endpoints.
12. Test the complete deployment in a staging environment.

## Troubleshooting

### Database URL errors

Check that `DATABASE_URL` is a valid SQLAlchemy URL. For local SQLite:

```text
sqlite:///smart_kitchen.db
```

### Missing model

Run:

```powershell
python ml/train.py
```

and confirm that `ml/model.pkl` exists. Verify that the training CSV is not empty and contains all required columns.

### Port already in use

Stop the existing development server or run the Flask app on another port using your preferred deployment configuration.

 