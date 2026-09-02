from flask import Blueprint, jsonify, request

from backend.services.gemini_service import generate_text


preparation_bp = Blueprint(
    "preparation",
    __name__,
    url_prefix="/api/preparation",
)


@preparation_bp.route("/", methods=["POST"])
def estimate_preparation():
    data = request.get_json(silent=True) or {}
    ingredients = str(data.get("ingredients", "")).strip()
    people = data.get("people")

    if not ingredients:
        return jsonify({
            "success": False,
            "message": "Please provide the available ingredients and quantities.",
        }), 400

    if len(ingredients) > 2000:
        return jsonify({
            "success": False,
            "message": "Ingredients must be 2,000 characters or fewer.",
        }), 400

    try:
        people = int(people)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Number of people must be a whole number.",
        }), 400

    if not 1 <= people <= 10000:
        return jsonify({
            "success": False,
            "message": "Number of people must be between 1 and 10,000.",
        }), 400

    prompt = f"""You are assisting a kitchen owner with an initial food-preparation estimate.
Number of people to serve: {people}
Available ingredients (including quantities supplied):
{ingredients}

Give a concise, practical response with these headings:
1. Suggested servings to prepare
2. Ingredient allocation or portions, only where supplied quantities support it
3. Assumptions and missing information
4. A conservative adjustment to reduce waste

Do not claim exact nutritional, safety, or inventory facts. If the ingredients or their
quantities do not identify a dish clearly enough, say so and explain what the owner
needs to confirm before preparing food."""

    estimate = generate_text(prompt)

    if estimate.startswith("[GEMINI ERROR]"):
        return jsonify({
            "success": False,
            "message": "Gemini could not generate a preparation estimate.",
        }), 503

    if estimate.startswith("[GEMINI MOCK]"):
        return jsonify({
            "success": False,
            "message": "Gemini is not configured. Add GEMINI_API_KEY to .env and restart the app.",
        }), 503

    return jsonify({
        "success": True,
        "estimate": estimate,
    })
