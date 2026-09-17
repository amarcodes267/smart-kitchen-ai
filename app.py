import os
import sys
import importlib.util

# Ensure AI-KITCHEN directory is in sys.path
ai_kitchen_dir = os.path.join(os.path.dirname(__file__), "AI-KITCHEN")
if ai_kitchen_dir not in sys.path:
    sys.path.insert(0, ai_kitchen_dir)

# Load the Flask app instance from AI-KITCHEN/app.py
inner_app_path = os.path.join(ai_kitchen_dir, "app.py")
spec = importlib.util.spec_from_file_location("ai_kitchen_app", inner_app_path)
module = importlib.util.module_from_spec(spec)
sys.modules["ai_kitchen_app"] = module
spec.loader.exec_module(module)

app = module.app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
