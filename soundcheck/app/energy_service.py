"""Appliance energy consumption and operating cost tool using WattFigure public API."""

import os
from typing import Any, Dict
import requests

WATTFIGURE_API_URL = "https://api.wattfigure.com/v1"

# Mapping common appliance terms to WattFigure catalog slugs
SLUG_MAP = {
    "washer": "washing-machine",
    "washing machine": "washing-machine",
    "dryer": "clothes-dryer",
    "clothes dryer": "clothes-dryer",
    "refrigerator": "refrigerator",
    "fridge": "refrigerator",
    "freezer": "chest-freezer",
    "dishwasher": "dishwasher",
    "oven": "electric-oven",
    "electric oven": "electric-oven",
    "air fryer": "air-fryer",
    "microwave": "microwave",
    "ac": "central-ac",
    "air conditioner": "central-ac",
    "hvac": "central-ac",
    "space heater": "space-heater",
    "water heater": "electric-water-heater",
}


def get_appliance_energy_cost(appliance: str, state: str = "California") -> Dict[str, Any]:
    """Retrieve real-world electricity rates and annual operating costs for a household appliance by US state.

    Fetches current state-by-state electricity rates (EIA data) and appliance energy consumption estimates
    from the WattFigure public API (from the public-apis directory).

    Args:
        appliance: Name or type of appliance (e.g. 'washing machine', 'dryer', 'refrigerator', 'dishwasher', 'microwave', 'hvac').
        state: US state name (e.g. 'California', 'Texas', 'New York', 'Florida'). Defaults to 'California'.

    Returns:
        A dictionary containing state electric rate, annual kWh, estimated monthly/annual running costs, and energy tips.
    """
    api_key = os.getenv("WATTFIGURE_API_KEY")
    headers = {"X-API-Key": api_key} if api_key else {}

    # Normalize appliance slug
    cleaned_name = appliance.lower().strip()
    slug = SLUG_MAP.get(cleaned_name)
    if not slug:
        for key, mapped_slug in SLUG_MAP.items():
            if key in cleaned_name:
                slug = mapped_slug
                break
    if not slug:
        slug = cleaned_name.replace(" ", "-")

    try:
        resp = requests.get(
            f"{WATTFIGURE_API_URL}/cost",
            params={"state": state.lower(), "appliance": slug},
            headers=headers,
            timeout=8,
        )
        if resp.status_code != 200:
            return {
                "error": f"WattFigure API returned status {resp.status_code}: {resp.text}",
                "appliance": appliance,
                "state": state,
            }

        data = resp.json()
        return {
            "appliance": data.get("appliance", slug),
            "state": data.get("state", state),
            "cents_per_kwh": data.get("cents_per_kwh"),
            "kwh_per_year": data.get("kwh_per_year"),
            "cost_per_month_usd": data.get("cost_per_month"),
            "cost_per_year_usd": data.get("cost_per_year"),
            "source": "WattFigure API (U.S. EIA Electric Power data)",
        }
    except Exception as e:
        return {"error": f"Failed to contact WattFigure API: {e}", "appliance": appliance, "state": state}
