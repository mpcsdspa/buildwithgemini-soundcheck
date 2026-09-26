"""Repair vs. Replace financial decision calculator for SoundCheck."""

from typing import Any, Dict

APPLIANCE_LIFESPANS = {
    "washing machine": 11,
    "washer": 11,
    "dryer": 13,
    "clothes dryer": 13,
    "refrigerator": 13,
    "fridge": 13,
    "dishwasher": 10,
    "hvac": 15,
    "air conditioner": 15,
    "lawnmower": 9,
    "microwave": 9,
}


def calculate_repair_vs_replace_roi(
    part_cost_usd: float,
    appliance_age_years: float,
    new_appliance_cost_usd: float,
    appliance_type: str = "general",
    diy: bool = True,
) -> Dict[str, Any]:
    """Calculate whether it is more financially sound to repair an appliance or replace it.

    Evaluates the appliance industry '50% Rule' (age vs. lifespan and repair cost vs. new unit cost).

    Args:
        part_cost_usd: Cost of the replacement part in USD.
        appliance_age_years: Current age of the appliance in years.
        new_appliance_cost_usd: Cost to purchase a new equivalent appliance in USD.
        appliance_type: Category of appliance (e.g. 'Washing Machine', 'Refrigerator', 'Dishwasher').
        diy: True if the user will perform the repair themselves ($0 labor), False if hiring a technician (~$120 labor).

    Returns:
        A dictionary with the repair recommendation, cost breakdown, and financial reasoning.
    """
    labor_cost = 0.0 if diy else 120.0
    total_repair_cost = round(float(part_cost_usd) + labor_cost, 2)
    new_cost = max(1.0, float(new_appliance_cost_usd))

    norm_type = appliance_type.lower()
    expected_lifespan = next(
        (span for key, span in APPLIANCE_LIFESPANS.items() if key in norm_type),
        10,
    )

    remaining_life = max(0.0, expected_lifespan - appliance_age_years)
    age_ratio = appliance_age_years / expected_lifespan
    cost_ratio = total_repair_cost / new_cost

    if (age_ratio >= 0.75) or (cost_ratio > 0.50) or (age_ratio >= 0.50 and cost_ratio > 0.40):
        recommendation = "REPLACE"
        rationale = (
            f"The appliance is at {age_ratio:.0%} of its expected {expected_lifespan}-year lifespan, "
            f"and the repair cost (${total_repair_cost:.2f}) is {cost_ratio:.0%} of a new replacement. "
            f"Replacing the appliance is more cost-effective long-term."
        )
    else:
        recommendation = "REPAIR"
        savings = round(new_cost - total_repair_cost, 2)
        rationale = (
            f"Repairing costs only ${total_repair_cost:.2f} ({cost_ratio:.0%} of new unit), "
            f"saving ${savings:.2f} while retaining approximately {remaining_life:.1f} years of useful life."
        )

    return {
        "recommendation": recommendation,
        "total_repair_cost_usd": total_repair_cost,
        "new_appliance_cost_usd": new_cost,
        "potential_savings_usd": max(0.0, round(new_cost - total_repair_cost, 2)),
        "appliance_age_years": appliance_age_years,
        "expected_lifespan_years": expected_lifespan,
        "remaining_lifespan_years": round(remaining_life, 1),
        "labor_mode": "DIY ($0 labor)" if diy else "Professional ($120 estimated labor)",
        "rationale": rationale,
    }
