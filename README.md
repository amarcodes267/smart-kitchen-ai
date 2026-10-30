# 🍽️ Smart Kitchen AI — Intelligent Commercial Kitchen Operations & Demand Forecasting Platform

<p align="center">
  <img src="AI-KITCHEN/static/images/hero-food-3d.png" alt="Smart Kitchen AI 3D Hero Render" width="750" style="border-radius: 20px; box-shadow: 0 20px 45px rgba(15, 23, 42, 0.12);" />
</p>

<p align="center">
  <strong>An enterprise-grade, AI-driven commercial kitchen management system designed to eliminate food waste, accurately forecast meal demand, automate inventory procurement, and optimize daily food preparation workflows.</strong>
</p>

<p align="center">
  <a href="#-key-features"><img src="https://img.shields.io/badge/Architecture-Modular%20MVC-059669?style=for-the-badge&logo=blueprint" alt="Architecture" /></a>
  <a href="#-tech-stack"><img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" /></a>
  <a href="#-tech-stack"><img src="https://img.shields.io/badge/Backend-Flask%20%2B%20SQLAlchemy-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" /></a>
  <a href="#-machine-learning-pipeline"><img src="https://img.shields.io/badge/ML%20Engine-XGBoost%20Regressor-FF6F00?style=for-the-badge&logo=xgboost&logoColor=white" alt="XGBoost" /></a>
  <a href="#-ai-recipe-studio--scaler"><img src="https://img.shields.io/badge/GenAI-Google%20Gemini-8E75C2?style=for-the-badge&logo=google&logoColor=white" alt="Gemini" /></a>
  <a href="#-testing--quality-assurance"><img src="https://img.shields.io/badge/Tests-29%20Passed%20%E2%9C%94-10B981?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License" /></a>
</p>

---

## 📑 Table of Contents

- [Executive Overview](#-executive-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Interactive Application Modules](#-interactive-application-modules)
- [Machine Learning & Prediction Engine](#-machine-learning--prediction-engine)
- [AI Recipe Studio & Deterministic Scaler](#-ai-recipe-studio--deterministic-scaler)
- [Kitchen Health Score Algorithm](#-kitchen-health-score-algorithm)
- [Complete REST API Reference](#-complete-rest-api-reference)
- [Tech Stack](#-tech-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Installation & Quickstart](#-installation--quickstart)
- [Environment Configuration](#-environment-configuration)
- [Model Training & Evaluation](#-model-training--evaluation)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Production Deployment & Hardening](#-production-deployment--hardening)
- [Contributing & License](#-contributing--license)

---

## 🌟 Executive Overview

In modern hospitality, ghost kitchens, and enterprise cafeterias, over-preparation leads to crippling food waste costs (typically 4–10% of total purchasing volume), while under-preparation causes stockouts, lost sales, and customer churn. 

**Smart Kitchen AI** resolves this imbalance by unifying:
1. **XGBoost Time-Series Forecasting**: Machine learning trained on temporal patterns, pricing elasticity, promotional schedules, and 7-day rolling sales trends to predict tomorrow's orders per dish.
2. **Inventory-Aware Preparation Optimization**: Translates predicted portion counts into real ingredient deductions, cross-referencing available storage to recommend non-wasteful prep targets.
3. **Generative Recipe Management**: Powered by **Google Gemini** with curated culinary fallbacks to standardize kitchen operating procedures (SOPs) and automatically calculate raw-material batch requirements.
4. **Operations Intelligence & Automated Procurement**: Auto-generates prioritized shopping lists and real-time alerts for expiring shelf life, stock deficits, and waste spikes.
9

---

## 🚀 Key Features

### 📈 Predictive Demand Forecasting
- **XGBoost Regression Engine**: Predicts order volumes per menu item based on day-of-week seasonality, historical lag sales, and promotional levers.
- **Chronological Temporal Split**: Evaluated on an 80/20 chronological time split to guarantee zero lookahead data leakage.
- **Dynamic Trend Indicators**: Surfaces volume velocity (increasing $\nearrow$, stable $\to$, or decreasing $\searrow$) directly on the dashboard.

### 🥦 Waste Tracking & Cost Analysis
- **Financial Waste Attribution**: Logs wasted portions with automated monetary loss calculations against unit costs.
- **Waste Reason Categorization**: Segregates losses by Over-Preparation, Spoilage/Expiration, Contamination, and Quality Defects.
- **Cost vs. Revenue Analysis**: Identifies top wasted items and projects weekly/monthly margin reclamation targets.

### 🍳 Generative AI Recipe Studio & Scaler
- **Structured Recipe Generation**: Generates culinary SOPs with ingredient breakdown, yields, prep/cook times, and step-by-step methods via Gemini API or instant domain knowledge fallback.
- **Deterministic Batch Scaler**: Dynamically scales ingredients to any portion volume ($N = 10, 50, 500$) without relying on LLM arithmetic hallucinations.
- **Live Inventory Matching**: Instantly checks raw ingredients against warehouse stock, highlighting deficits with one-click stock registry.

### 📦 Inventory Intelligence & Smart Procurement
- **Threshold-Driven Depletion Tracking**: Continuously calculates days-of-supply based on burn velocity and current stock.
- **Automated Shopping List Generator**: Classifies ingredients into **High Priority** (critical/out-of-stock), **Medium Priority** (below reorder point), and **Excess** (flagged to prevent over-purchasing).
- **One-Click Restock Pipeline**: Seamlessly replenishes inventory batches directly from procurement suggestions.

### 🛡️ 100-Point Kitchen Health Score
- **Multi-Factor Operational Index**: Synthesizes kitchen hygiene, cost efficiency, stock availability, and waste containment into an algorithmic score ($0 - 100$) with dynamic tier status (Grade A/B/C/D).

### 🔮 What-If Scenario Simulator
- **Demand Shock Testing**: Simulates $+10\%$, $+25\%$, $+50\%$ volume spikes to gauge inventory feasibility and required overtime prep.
- **Prep Reduction Analysis**: Models cost savings and stockout risks when strategically throttling prep quantities.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Client["Presentation Layer (Client Browser)"]
        UI["Modern Light SaaS UI (HTML5 / Vanilla JS / CSS3)"]
        Charts["Interactive Visualizations (Chart.js 4)"]
        Forms["Asynchronous REST Dispatchers (Fetch API)"]
    end

    subgraph Gateway["Application Layer (Flask WSGI)"]
        Router["App Router & Template Controllers (app.py)"]
        CORS["Cross-Origin & Cache Control Middleware"]
        Auth["Kitchen Context & Session Handlers"]
    end

    subgraph API["RESTful Services Layer (/api/*)"]
        R_Kitchen["Kitchen Blueprint"]
        R_Menu["Menu Blueprint"]
        R_Inv["Inventory Intelligence Blueprint"]
        R_Sales["Sales & Demand Blueprint"]
        R_Waste["Waste Tracking Blueprint"]
        R_Recipe["Recipe & Scaler Blueprint"]
        R_Health["Health Score Blueprint"]
        R_WhatIf["What-If Scenario Blueprint"]
    end

    subgraph Intelligence["AI & Machine Learning Engine"]
        XGB["XGBoost Regressor (ml/model.pkl)"]
        FeatureEngine["Feature Engineering & Preprocessing"]
        Gemini["Google Gemini Pro / Flash LLM API"]
        KB["Curated Culinary Knowledge Base Fallback"]
    end

    subgraph DataLayer["Persistence Layer"]
        ORM["SQLAlchemy ORM (9 Relational Models)"]
        DB[("SQLite 3 (Dev) / PostgreSQL (Prod)")]
        DataStore["Raw & Processed Datasets (CSV)"]
    end

    Client -->|HTTP / HTTPS| Gateway
    Gateway --> API
    API --> Intelligence
    API --> DataLayer
    Intelligence --> DataStore
    Intelligence --> ORM
    ORM --> DB
```

---

## 🖥️ Interactive Application Modules

The application delivers 13 responsive, production-ready interfaces:

| Module | Route | Purpose & Key Metrics |
| :--- | :--- | :--- |
| **Landing Page** | `/` | Platform introduction, 3D interactive hero presentation, product capabilities, and instant navigation. |
| **Executive Dashboard** | `/dashboard` | Daily prep recommendations, active kitchen KPIs, live demand bar charts, and waste distribution doughnuts. |
| **Kitchen Setup** | `/kitchen-setup` | Multi-kitchen creation, configuration, operational capacity, and active context switcher. |
| **Menu Studio** | `/menu` | Recipe linkage, menu item catalog, pricing, cost-per-serving, and dish categorization. |
| **Recipe Management & Scaler** | `/recipes` | AI recipe generator, interactive step editor, ingredient linker, and deterministic batch volume scaler. |
| **Inventory Hub** | `/inventory` | Raw material tracking, unit quantities, expiration tracking, minimum safety thresholds, and quick-restock drawer. |
| **Sales & Orders** | `/sales` | Historical orders log, revenue aggregation, channel breakdown (Dine-in, Takeaway, Online), and order entry. |
| **Food Waste Tracking** | `/waste` | Discard logging, waste classification (spoilage/over-prep), cost impact tracking, and reduction targets. |
| **Demand Predictions** | `/predictions` | XGBoost forecasting interface, parameter sliders (promotions, price adjustments), and prep suggestions. |
| **Business Analytics** | `/analytics` | Revenue trends, period filtering (7d, 30d, 90d, 365d), sales velocity, and gross profit margins. |
| **Live Operational Alerts** | `/alerts` | Critical/Warning/Info operational feeds for low stock, waste anomalies, and shelf-life warnings. |
| **Kitchen Health Score** | `/health-score` | Circular radial gauge scoring kitchen health across 5 weighted dimensions with actionable improvements. |
| **Smart Shopping List** | `/shopping` | Automatically compiled reorder lists sorted by urgency with one-click inventory replenishment. |

---

## 🧠 Machine Learning & Prediction Engine

The platform features an end-to-end machine learning pipeline built on **XGBoost (Extreme Gradient Boosting)**, engineered specifically for commercial kitchen demand dynamics.

### 1. Feature Engineering (`ml/preprocessing.py`)
- **Calendar & Seasonality**: Day of week (`0-6`), Month (`1-12`), Weekend indicator (`is_weekend`).
- **Pricing Dynamics**: Base price, checkout price, discount ratio (`checkout_price / base_price`), and promotional elasticity.
- **Promotional Signals**: Emailer promotions (`emailer_for_promotion`), Homepage display features (`homepage_featured`).
- **Lag & Moving Averages**: 7-day trailing average volume and volume lag indicators to capture recent trends.

### 2. Temporal Validation Strategy
Unlike standard random cross-validation which introduces lookahead leakage in time-series data, the training pipeline implements a **strict 80/20 chronological train-test split**.

```python
# ml/train.py snippet
cutoff_date = X["date"].quantile(0.8)
train_mask = X["date"] <= cutoff_date
test_mask = X["date"] > cutoff_date

X_train, y_train = X.loc[train_mask, features], y[train_mask]
X_test, y_test = X.loc[test_mask, features], y[test_mask]
```

### 3. Training & Performance Metrics
Models are automatically evaluated against standard regression metrics:
- **Mean Absolute Error (MAE)**: Measures average portion deviation.
- **Root Mean Squared Error (RMSE)**: Penalizes severe forecast misses.
- **Coefficient of Determination ($R^2$)**: Quantifies explained variance.

---

## 🍳 AI Recipe Studio & Deterministic Scaler

The recipe subsystem bridges generative AI and deterministic kitchen operations:

1. **Structured Recipe Creation**:
   - Uses `google-generativeai` (Gemini) to generate culinary recipes into structured JSON schemas (dish name, category, yields, preparation steps, ingredients, units, and storage directions).
   - If no API key is supplied, the platform falls back to an internal **Curated Domain Knowledge Base** containing comprehensive commercial recipes (Biryani, Samosas, Pasta, Burgers, Curries, etc.).

2. **Deterministic Mathematical Scaler**:
   - Prevents AI hallucination during high-volume prep by calculating ingredient scaling deterministically:
     $$\text{Required Quantity} = \left(\frac{\text{Target Portions}}{\text{Base Yield}}\right) \times \text{Base Quantity}$$
   - Compares required amounts against current inventory balances and immediately highlights any stock deficits prior to production.

---

# 📊 Kitchen Health Score Algorithm

The **Kitchen Health Score** ($0 - 100$) evaluates kitchen operational efficiency across 5 weighted pillars:

$$\text{Health Score} = 0.25 W_s + 0.20 I_s + 0.20 D_s + 0.20 C_s + 0.15 S_s$$

| Pillar | Weight | Metric Measured | Calculation Logic |
| :--- | :---: | :--- | :--- |
| **Waste Efficiency ($W_s$)** | $25\%$ | Waste-to-order ratio | $\max(0, 100 - (\text{Waste Rate} \times 2))$ |
| **Inventory Health ($I_s$)** | $20\%$ | Items below safety stock | $100 - \left(\frac{\text{Low Stock Items}}{\text{Total Inventory}} \times 100\right)$ |
| **Demand Fulfillment ($D_s$)** | $20\%$ | Order velocity & prep volume | Scaled order velocity against target throughput |
| **Cost Efficiency ($C_s$)** | $20\%$ | Waste financial loss vs revenue | $\max\left(0, 100 - \left(\frac{\text{Waste Cost}}{\text{Revenue}} \times 100\right)\right)$ |
| **Stock Availability ($S_s$)** | $15\%$ | Menu item fulfillability | Active menu items with $100\%$ raw ingredient availability |

---

## 🔌 Complete REST API Reference

All endpoints return standardized JSON payloads with `"success": true|false`.

### Kitchen Management (`/api/kitchen`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/kitchen/` | List all registered commercial kitchens |
| `POST` | `/api/kitchen/` | Create a new kitchen profile (`name`, `location`, `capacity`) |
| `GET` | `/api/kitchen/<id>` | Fetch kitchen details by ID |
| `PUT` | `/api/kitchen/<id>` | Update kitchen information |
| `DELETE` | `/api/kitchen/<id>` | Remove a kitchen record |

### Menu Management (`/api/menu`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/menu/kitchen/<kitchen_id>` | List all menu dishes for a specific kitchen |
| `POST` | `/api/menu/` | Add menu item (`name`, `category`, `selling_price`, `cost_per_serving`) |
| `PUT` | `/api/menu/<id>` | Edit menu item details |
| `DELETE` | `/api/menu/<id>` | Delete menu item |

### Inventory Intelligence (`/api/inventory`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/inventory/kitchen/<kitchen_id>` | List current stock items and threshold warnings |
| `POST` | `/api/inventory/` | Add stock item (`ingredient_name`, `quantity`, `unit`, `minimum_stock`) |
| `PUT` | `/api/inventory/<id>` | Update stock count or reorder threshold |
| `DELETE` | `/api/inventory/<id>` | Delete inventory item |
| `GET` | `/api/inventory-intelligence/kitchen/<id>` | Calculate inventory burn rates and days-of-supply |

### Demand Forecasting (`/api/prediction` & `/api/demand`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/prediction/` | Run model prediction for specific dish parameters |
| `GET` | `/api/demand/kitchen/<kitchen_id>` | Retrieve 14-day predicted demand for all active dishes |
| `POST` | `/api/preparation/` | Generate smart ingredient preparation guide |

### Recipe Management (`/api/recipe`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/recipe/generate` | Generate AI recipe draft with live inventory matching |
| `POST` | `/api/recipe/` | Commit reviewed recipe and ingredients to database |
| `GET` | `/api/recipe/kitchen/<kitchen_id>` | Retrieve all saved kitchen recipes |
| `GET` | `/api/recipe/<id>` | Get specific recipe details with ingredients |
| `POST` | `/api/recipe/<id>/scale` | Calculate scaled batch requirements for target portions |
| `DELETE` | `/api/recipe/<id>` | Remove recipe record |

### Waste & Analytics (`/api/waste` & `/api/analytics`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/waste/kitchen/<kitchen_id>` | Retrieve historical waste records |
| `POST` | `/api/waste/` | Log new waste event (`menu_item_id`, `quantity_wasted`, `reason`) |
| `GET` | `/api/waste/summary/kitchen/<id>` | Summarize waste metrics and cost losses |
| `GET` | `/api/analytics/sales/kitchen/<id>` | Get sales trends and revenue metrics |
| `GET` | `/api/analytics/menu/kitchen/<id>` | Analyze menu dish profitability and velocity |

### Executive Insights (`/api/health-score`, `/api/shopping`, `/api/whatif`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health-score/kitchen/<id>` | Compute real-time 100-point Health Score breakdown |
| `GET` | `/api/shopping/kitchen/<id>` | Generate prioritized procurement shopping list |
| `POST` | `/api/whatif/demand-increase` | Simulate $+X\%$ demand surge scenario |
| `POST` | `/api/whatif/preparation-reduction`| Simulate $-X\%$ preparation reduction scenario |
| `GET` | `/api/alerts/kitchen/<id>` | Fetch operational alerts and notifications |

---

## 💻 Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Chart.js 4, Plus Jakarta Sans Typography |
| **Backend Framework** | Python 3.12, Flask 3.x, Werkzeug |
| **Database & ORM** | SQLAlchemy, SQLite 3 (Development), PostgreSQL + Psycopg2 (Production) |
| **Machine Learning** | XGBoost Regressor, Scikit-Learn, Pandas, NumPy, Joblib |
| **Generative AI** | Google Gemini API (`google-generativeai`) + Curated Culinary Fallback Engine |
| **Testing & Tooling** | Pytest, Pytest-Cov, Unittest Mock |
| **Deployment / WSGI** | Gunicorn, Waitress, Python venv |

---

## 📂 Project Directory Structure

```text
smart-kitchen-ai/
├── app.py                             # Root application bootstrap launcher
├── run.bat                            # Windows one-click desktop launcher
├── requirements.txt                   # Production Python dependencies
├── .env.example                       # Environment variables template
├── .gitignore                         # Excluded databases, venv, and cache files
├── README.md                          # Comprehensive project documentation
│
└── AI-KITCHEN/                        # Core Application Package
    ├── app.py                         # Flask app factory, CORS, and page routes
    ├── smart_kitchen.db               # Local SQLite operational database
    │
    ├── backend/                       # Backend Business Logic & API
    │   ├── models/                    # 9 Relational SQLAlchemy Database Models
    │   │   ├── kitchen.py             # Commercial kitchen entity
    │   │   ├── menu.py                # Menu item definitions & prices
    │   │   ├── inventory.py           # Raw ingredient stock tracking
    │   │   ├── sales.py               # Historical customer order records
    │   │   ├── waste.py               # Discarded portion logs & reasons
    │   │   ├── recipe.py              # Culinary recipes & ingredient links
    │   │   ├── prediction.py          # Recorded demand forecasts
    │   │   └── alert.py               # Operational notification entries
    │   ├── routes/                    # 16 Flask REST API Blueprints
    │   ├── services/                  # Business logic (Health score, What-If, etc.)
    │   └── utils/                     # Configuration and database connection helpers
    │
    ├── ml/                            # Machine Learning Subsystem
    │   ├── train.py                   # XGBoost training pipeline with temporal split
    │   ├── preprocessing.py           # Feature engineering and cleaning
    │   ├── predict.py                 # Real-time inference utilities
    │   ├── model.pkl                  # Trained model binary (Joblib)
    │   └── model.json                 # Native XGBoost model export
    │
    ├── data/                          # Dataset Repositories
    │   ├── raw/                       # Daily sales & historical demand CSVs
    │   └── processed/                 # Engineered feature matrices
    │
    ├── static/                        # Frontend Static Assets
    │   ├── css/                       # Modular Stylesheets (Light SaaS theme)
    │   │   ├── style.css              # Global tokens, typography, navbar, buttons
    │   │   ├── dashboard.css          # Metric cards and KPI grids
    │   │   ├── forms.css              # Input controls, selects, search bars
    │   │   └── responsive.css         # Mobile and tablet breakpoints
    │   ├── js/                        # Client-side scripts & charts
    │   │   └── charts.js              # Chart.js line, bar, doughnut configurations
    │   └── images/                    # Visual assets
    │       ├── hero-food-3d.png       # Custom 3D food render (Hero showcase)
    │       └── hero-food.png          # Fallback image asset
    │
    ├── templates/                     # 13 Production HTML5 Jinja2 Templates
    │   ├── index.html                 # Platform landing page
    │   ├── dashboard.html             # Executive operational dashboard
    │   ├── kitchen_setup.html         # Kitchen configuration
    │   ├── menu.html                  # Menu item management
    │   ├── recipes.html               # Recipe generator & batch scaler
    │   ├── inventory.html             # Inventory tracking
    │   ├── sales.html                 # Sales order log
    │   ├── waste.html                 # Food waste recording
    │   ├── predictions.html           # Demand prediction studio
    │   ├── analytics.html             # Financial & volume analytics
    │   ├── alerts.html                # Live operational alerts
    │   ├── health_score.html          # Kitchen Health Score gauge
    │   └── shopping.html              # Smart procurement shopping list
    │
    └── tests/                         # Automated Pytest Suite
        ├── test_api.py                # REST API endpoint unit tests
        ├── test_recipe.py             # Recipe generation & scaler tests
        ├── test_inventory.py          # Stock depletion tests
        ├── test_prediction.py         # ML prediction pipeline tests
        ├── test_e2e.py                # End-to-end user journey tests
        └── test_qa_comprehensive.py   # Comprehensive regression test suite
```

---

## ⚡ Installation & Quickstart

### Prerequisites
- **Python 3.10+** (Tested on Python 3.12.10)
- **Git**
- Optional: Virtual environment manager (`venv`)

### 1. Clone the Repository
```bash
git clone https://github.com/amarcodes267/smart-kitchen-ai.git
cd smart-kitchen-ai
```

### 2. Set Up Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

*Note: If PowerShell execution policy restricts scripts, execute:*
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the template and configure your local settings:
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

*(Refer to [Environment Configuration](#-environment-configuration) for parameter details).*

### 5. Launch the Application

**Option A — Windows One-Click Launcher:**
Double-click `run.bat` or run:
```cmd
run.bat
```

**Option B — Direct Command Line:**
```bash
python app.py
```

The web server will start locally at:
👉 **`http://127.0.0.1:5000`**

---

## ⚙️ Environment Configuration

Configuration is managed via `.env` files located in the root or `AI-KITCHEN/` directory:

```env
# Application Settings
SECRET_KEY=your-secure-random-secret-key-here
FLASK_DEBUG=True
PORT=5000

# Database Connection (SQLite default for local dev)
DATABASE_URL=sqlite:///smart_kitchen.db

# For Production PostgreSQL:
# DATABASE_URL=postgresql://username:password@localhost:5432/smart_kitchen

# Generative AI (Optional for Gemini Recipe Creation)
GEMINI_API_KEY=your-gemini-api-key-here
```

> **Security Note**: Never commit your actual `.env` file containing sensitive credentials to source control. `.env` is included in `.gitignore`.

---

## 🎯 Model Training & Evaluation

To retrain the demand forecasting model on updated kitchen sales logs:

```bash
# From the project root
python AI-KITCHEN/ml/train.py
```

**Training Process Output:**
```text
===================================
      AI KITCHEN MODEL TRAINING
===================================

Preparing training data...
Loading daily kitchen sales dataset from: AI-KITCHEN/data/raw/kitchen_sales_daily.csv
Loaded 2200 records.

Total records: 2200
Total features: 12

Applying chronological temporal split (80% train / 20% test)...
Cutoff date: 2026-08-15
Training XGBoost Regressor...
Model saved to: AI-KITCHEN/ml/model.pkl
Native JSON model saved to: AI-KITCHEN/ml/model.json

Test Set Performance:
  Mean Absolute Error (MAE): 4.12 portions
  Root Mean Squared Error (RMSE): 5.86 portions
  R-squared Score (R²): 0.892
===================================
```

---

## 🧪 Testing & Quality Assurance

The codebase includes an automated test suite verifying all HTML routes, REST endpoints, model inference, and edge cases.

To execute the entire test suite:
```bash
python -m pytest AI-KITCHEN/tests -v
```

**Test Execution Summary:**
```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Asus\Desktop\smart-kitchen-ai
collected 29 items

AI-KITCHEN\tests\test_api.py ....                                        [ 13%]
AI-KITCHEN\tests\test_e2e.py ..                                          [ 20%]
AI-KITCHEN\tests\test_inventory.py .                                     [ 24%]
AI-KITCHEN\tests\test_prediction.py .....                                [ 41%]
AI-KITCHEN\tests\test_qa_comprehensive.py ...........                    [ 79%]
AI-KITCHEN\tests\test_recipe.py ......                                   [100%]

============================= 29 passed in 4.85s ==============================
```

---

## 🛡️ Production Deployment & Hardening

When transitioning from local development to production hosting:

1. **Production WSGI Server**:
   Do not run the Flask built-in server in production. Run with **Gunicorn** (Linux) or **Waitress** (Windows):
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
2. **Managed Database**:
   Switch from local SQLite to managed PostgreSQL by setting `DATABASE_URL=postgresql://user:pass@host:5432/dbname`.
3. **Turn Off Debugging**:
   Set `FLASK_DEBUG=False` in environment variables.
4. **Enforce HTTPS / Reverse Proxy**:
   Deploy behind Nginx, Cloudflare, or AWS ALB with SSL/TLS termination and HTTP Strict Transport Security (HSTS).
5. **Secret Rotation**:
   Set a cryptographically strong `SECRET_KEY` via secret managers (AWS Secrets Manager, HashiCorp Vault, or GitHub Secrets).

---

## 🤝 Contributing & License

Contributions, issues, and feature requests are welcome!

1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

### 📄 License
Distributed under the **MIT License**. See `LICENSE` for more information.

---

<p align="center">
  Built with ❤️ for sustainable, zero-waste commercial culinary operations.<br />
  <strong>Smart Kitchen AI © 2026. All Rights Reserved.</strong>
</p>
