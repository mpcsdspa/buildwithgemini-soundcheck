"""Firestore backend service for SoundCheck parts catalog and diagnostics."""

from typing import Any, Dict, List, Optional
from google.cloud import firestore

# IMPORTANT: Hardcoded project ID as required to avoid project number resolution issues on Agent Platform
PROJECT_ID = "qwiklabs-gcp-04-9b2fabbcbad5"
COLLECTION_NAME = "parts_catalog"


def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client instance configured with the explicit project ID."""
    return firestore.Client(project=PROJECT_ID)


def search_parts_catalog(query: str = "", appliance_type: str = "") -> List[Dict[str, Any]]:
    """Search the replacement parts catalog in Firestore by acoustic symptom, defect, or appliance type.

    Args:
        query: Keywords describing the sound/symptom (e.g. "squealing", "grinding", "humming", "vibration")
               or the defect/part name (e.g. "belt", "pump", "capacitor").
        appliance_type: Optional filter by appliance category (e.g. "Washing Machine", "Refrigerator",
                        "Dishwasher", "Clothes Dryer", "HVAC / Air Conditioner", "Lawnmower").

    Returns:
        A list of matching replacement parts from the Firestore catalog.
    """
    db = get_firestore_client()
    docs = db.collection(COLLECTION_NAME).stream()

    results = []
    q_lower = query.lower().strip()
    app_lower = appliance_type.lower().strip()

    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue

        # Filter by appliance type if specified
        if app_lower:
            doc_app = str(data.get("appliance_type", "")).lower()
            if app_lower not in doc_app and doc_app not in app_lower:
                continue

        # If query is provided, match against searchable fields
        if q_lower:
            searchable_text = " ".join([
                str(data.get("part_name", "")),
                str(data.get("sound_symptom", "")),
                str(data.get("defect_cause", "")),
                str(data.get("oem_number", "")),
                str(data.get("appliance_type", "")),
            ]).lower()
            if q_lower not in searchable_text:
                continue

        results.append(data)

    return results


def get_part_details(part_id: str) -> Dict[str, Any]:
    """Retrieve detailed specifications and repair info for a specific part by its part ID.

    Args:
        part_id: The unique identifier of the part (e.g. "WP-BELT-107", "FRIDGE-FAN-440", "DISH-PUMP-812").

    Returns:
        A dictionary containing the part's full details, or an error status if not found.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(part_id)
    doc = doc_ref.get()

    if not doc.exists:
        return {"error": f"Part '{part_id}' not found in the Firestore catalog."}

    return doc.to_dict() or {}


def add_part_to_catalog(
    part_id: str,
    part_name: str,
    appliance_type: str,
    sound_symptom: str,
    defect_cause: str,
    oem_number: str,
    price_usd: float,
    in_stock: bool = True,
    difficulty: str = "Intermediate",
    tutorial_url: str = "",
) -> Dict[str, Any]:
    """Add a new replacement part or update an existing part in the Firestore catalog.

    Args:
        part_id: Unique identifier for the part (e.g. "MICROWAVE-FUSE-101").
        part_name: Human-readable name of the component.
        appliance_type: Category of appliance (e.g. "Microwave", "Washing Machine").
        sound_symptom: Acoustic description of the malfunction (e.g. "Loud humming then sudden silence").
        defect_cause: Root mechanical or electrical cause of the failure.
        oem_number: Manufacturer / OEM part number.
        price_usd: Estimated price in USD.
        in_stock: Whether the part is currently in stock.
        difficulty: Repair difficulty rating (e.g. "Beginner (15 mins)", "Intermediate (45 mins)").
        tutorial_url: Link to a repair tutorial or manual.

    Returns:
        A dictionary confirming the part was saved to Firestore.
    """
    db = get_firestore_client()
    part_data = {
        "part_id": part_id,
        "part_name": part_name,
        "appliance_type": appliance_type,
        "sound_symptom": sound_symptom,
        "defect_cause": defect_cause,
        "oem_number": oem_number,
        "price_usd": float(price_usd),
        "in_stock": in_stock,
        "difficulty": difficulty,
        "tutorial_url": tutorial_url,
    }

    db.collection(COLLECTION_NAME).document(part_id).set(part_data)
    return {"status": "success", "message": f"Part '{part_id}' successfully saved to Firestore.", "part": part_data}


def update_part_inventory(part_id: str, in_stock: bool, price_usd: Optional[float] = None) -> Dict[str, Any]:
    """Update stock availability and optionally the price of an existing part in Firestore.

    Args:
        part_id: The unique identifier of the part to update.
        in_stock: Updated availability boolean.
        price_usd: Optional new price in USD.

    Returns:
        A dictionary confirming the update status.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(part_id)
    doc = doc_ref.get()

    if not doc.exists:
        return {"error": f"Part '{part_id}' not found in the Firestore catalog."}

    updates: Dict[str, Any] = {"in_stock": in_stock}
    if price_usd is not None:
        updates["price_usd"] = float(price_usd)

    doc_ref.update(updates)
    return {"status": "success", "message": f"Part '{part_id}' updated.", "updates": updates}
