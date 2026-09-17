import json
import math
import re
from backend.utils.config import Config

# Lightweight wrapper around an external LLM (Gemini) with domain fallback.
# When no API key is configured or offline, high-quality domain generators
# provide realistic culinary operational guidance.

def generate_text(prompt: str, max_tokens: int = 256) -> str:
    """Generate text using Gemini if configured, otherwise return a mock response.

    Returns:
        str: Generated text or fallback string.
    """
    api_key = getattr(Config, 'GEMINI_API_KEY', '').strip()

    if not api_key or not api_key.startswith("AIzaSy"):
        # Demo fallback
        return f"[GEMINI MOCK] {prompt}"

    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            prompt,
            generation_config={"max_output_tokens": max_tokens},
            request_options={"timeout": 10},
        )
        return getattr(response, 'text', str(response))
    except Exception as e:
        # Fail gracefully in production -- return short error string
        return f"[GEMINI ERROR] {e}"


def generate_prediction_explanation(
    item_name: str,
    predicted_demand: float,
    trend: str = "stable",
    trend_symbol: str = "→",
    change_pct: float = 0.0,
    previous_avg: float = 0.0,
    recent_avg: float = 0.0,
    safety_buffer_pct: float = 0.05,
) -> dict:
    """Generate an AI explanation and practical kitchen recommendation for an XGBoost forecast.

    The numerical prediction is strictly computed by XGBoost; this function
    interprets the number and converts it into operational culinary guidance.
    """
    pred_val = float(predicted_demand or 0.0)
    prep_target = max(0, int(math.ceil(pred_val * (1.0 + safety_buffer_pct))))
    buffer_units = max(0, prep_target - int(math.floor(pred_val)))
    batch_size = max(5, int(math.ceil(prep_target / 3))) if prep_target > 10 else prep_target

    api_key = getattr(Config, 'GEMINI_API_KEY', '').strip()

    # Attempt live Gemini LLM call if valid API key is present
    if api_key and api_key.startswith("AIzaSy"):
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = f"""You are an executive chef and smart kitchen operational AI assistant.
An ML model (XGBoost) has completed its numerical demand forecast for tomorrow.
IMPORTANT: Do NOT calculate or alter the numerical prediction. The ML model has already determined the forecast.

Input Data:
- Food Item: {item_name}
- XGBoost Predicted Demand: {pred_val} expected orders
- Sales Trend: {trend} ({trend_symbol})
- Sales Change: {change_pct}%
- Previous Period Average: {previous_avg} orders/day
- Recent Period Average: {recent_avg} orders/day
- Suggested Prep Target: {prep_target} units (includes a {int(safety_buffer_pct * 100)}% safety buffer of ~{buffer_units} units)

Your task:
1. Prediction Explanation: In 1-2 concise sentences, explain why the XGBoost model predicted {pred_val} orders, citing the sales velocity, trend, and recent performance patterns.
2. Practical Kitchen Recommendation: In 2-3 actionable sentences, convert this forecast into practical kitchen advice (batch cooking schedule, prep timing, station staging, and waste minimization tips).

Respond strictly in valid JSON format with keys "explanation" and "kitchen_recommendation":
{{
  "explanation": "...",
  "kitchen_recommendation": "..."
}}
"""
            response = model.generate_content(
                prompt,
                generation_config={"max_output_tokens": 350, "temperature": 0.4},
                request_options={"timeout": 6},
            )
            raw_text = getattr(response, "text", "").strip()
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                if "explanation" in data and "kitchen_recommendation" in data:
                    return {
                        "explanation": data["explanation"].strip(),
                        "kitchen_recommendation": data["kitchen_recommendation"].strip(),
                        "recommended_prep": prep_target,
                        "safety_buffer_units": buffer_units,
                        "source": "gemini",
                    }
        except Exception:
            pass  # Fall through to domain-specific generative fallback

    # Domain generative fallback (fast, deterministic, realistic culinary advice)
    clean_name = item_name.strip() if item_name else "Menu Item"
    item_lower = clean_name.lower()

    # 1. Explanation of XGBoost numerical prediction
    if trend == "increasing":
        explanation = (
            f"The XGBoost model projects {pred_val} orders for {clean_name} tomorrow, "
            f"reflecting a strong {abs(round(change_pct, 1))}% surge in recent sales velocity "
            f"relative to the previous baseline of {round(previous_avg, 1)} orders/day. "
            f"The model's rolling momentum and day-of-week weights anticipate high order volume."
        )
    elif trend == "decreasing":
        explanation = (
            f"The XGBoost model forecasts {pred_val} orders for {clean_name} tomorrow, "
            f"accounting for a {abs(round(change_pct, 1))}% softening in recent sales volume "
            f"compared to the prior baseline of {round(previous_avg, 1)} orders/day. "
            f"The model lowers target production to guard against kitchen overprep and spoilage."
        )
    else:
        explanation = (
            f"The XGBoost model forecasts {pred_val} orders for {clean_name} tomorrow, "
            f"consistent with stable ordering patterns and a modest {round(change_pct, 1)}% variance "
            f"around the recent average of {round(recent_avg, 1)} orders/day. "
            f"Lagged features confirm steady baseline consumption."
        )

    # 2. Practical kitchen recommendation tailored to dish characteristics
    if any(k in item_lower for k in ["samosa", "pakora", "fry", "roll", "snack", "nugget"]):
        recommendation = (
            f"Prepare approximately {prep_target} units (incorporating a {int(safety_buffer_pct * 100)}% "
            f"safety margin of ~{buffer_units} portions). Complete pastry folding and savory filling mise en place "
            f"during morning prep, then fry in rolling batches of ~{batch_size} portions during peak lunch and evening rush. "
            f"Hold fried items under display warmers for a maximum of 40 minutes to preserve crispness and prevent waste."
        )
    elif any(k in item_lower for k in ["biryani", "rice", "pulao", "khichdi"]):
        recommendation = (
            f"Target {prep_target} portions (including ~{buffer_units} portions safety buffer). "
            f"Stage proteins and parboiled grains during morning prep; cook in {max(2, prep_target // 20)} staggered "
            f"dum batches aligned with 12:30 PM and 7:30 PM peak service windows. Hold active batches in insulated warmers "
            f"above 65°C and chill any unserved portions at end of service following HACCP protocols."
        )
    elif any(k in item_lower for k in ["curry", "paneer", "dal", "gravy", "soup", "tikka", "chicken"]):
        recommendation = (
            f"Prepare {prep_target} portions total (including a {int(safety_buffer_pct * 100)}% buffer of ~{buffer_units} portions). "
            f"Simmer mother gravies and portion marinated proteins during early mise en place, finishing orders in small pans on the line. "
            f"Rapid-chill unsold base gravy in an ice-water bath before refrigeration for safe, zero-waste reuse tomorrow."
        )
    elif any(k in item_lower for k in ["roti", "naan", "paratha", "bread", "pizza", "burger"]):
        recommendation = (
            f"Target ingredients for {prep_target} portions (with {buffer_units} buffer units). "
            f"Portion and proof dough during morning prep, then bake or cook strictly to order during service. "
            f"Store unused pre-portioned dough in airtight chilled containers to prevent drying and food waste."
        )
    else:
        recommendation = (
            f"Target preparing {prep_target} portions (includes a {int(safety_buffer_pct * 100)}% safety buffer of ~{buffer_units} portions). "
            f"Complete core vegetable and protein prep during early shift, cooking in rolling batches of ~{batch_size} portions "
            f"during peak demand windows. Actively monitor ticket velocity to taper off production towards shift close."
        )

    return {
        "explanation": explanation,
        "kitchen_recommendation": recommendation,
        "recommended_prep": prep_target,
        "safety_buffer_units": buffer_units,
        "source": "domain_ai",
    }

