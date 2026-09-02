# README for AI-KITCHEN

# AI-KITCHEN

This repository contains a sample AI-driven kitchen management demo. It includes a Flask backend, a simple frontend, and a small ML pipeline to predict demand and produce basic recommendations.

Quick start
1. Create a virtual environment and install requirements: python -m pip install -r requirements.txt
2. Provide a dataset at data/raw/kitchen_data.csv (see ml/preprocessing.py for required columns). A synthetic dataset can be generated if needed.
3. Train model: python ml/train.py
4. Start the app: python app.py

Notes
- For local development the app uses SQLite by default (see backend/utils/config.py).
- ML artifacts are saved to ml/model.pkl
- Use the /health endpoint to check server status.

Deploy on Render
1. Push this repository to GitHub.
2. In Render, choose New > Blueprint and select the repository. Render will use the root `render.yaml` file to create the web service and PostgreSQL database.
3. Add `GEMINI_API_KEY` in the Render service environment if preparation estimates should use Gemini. It is optional; the app has a fallback response.
4. Deploy. The service starts with Gunicorn and exposes `/health` for health checks.

The Render database keeps kitchens, menus, sales, and other application data across deploys. Do not set `FLASK_DEBUG=True` in production.
