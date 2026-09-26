"""Seed Firestore with initial replacement parts catalog for SoundCheck."""

from google.cloud import firestore

# IMPORTANT: Hardcoded project ID as required to avoid project number resolution issues on Agent Platform
PROJECT_ID = "qwiklabs-gcp-04-9b2fabbcbad5"
COLLECTION_NAME = "parts_catalog"

SEEDED_PARTS = [
    {
        "part_id": "WP-BELT-107",
        "part_name": "Heavy-Duty Washer Drive Belt",
        "appliance_type": "Washing Machine",
        "sound_symptom": "High-pitched squealing, screeching, or rhythmic slipping sound during spin cycle",
        "defect_cause": "Worn, stretched, or glazed drive belt slipping against motor drive pulley",
        "oem_number": "WPW10721967",
        "price_usd": 24.95,
        "in_stock": True,
        "difficulty": "Beginner (25 mins)",
        "tutorial_url": "https://tutorials.soundcheck.dev/washer-belt",
    },
    {
        "part_id": "FRIDGE-FAN-440",
        "part_name": "Evaporator Fan Motor Assembly",
        "appliance_type": "Refrigerator",
        "sound_symptom": "Loud humming, buzzing, groaning, or chirping from freezer compartment that stops when door opens",
        "defect_cause": "Worn motor sleeve bearings or heavy frost accumulation contacting fan blades",
        "oem_number": "WR60X10307",
        "price_usd": 49.99,
        "in_stock": True,
        "difficulty": "Intermediate (45 mins)",
        "tutorial_url": "https://tutorials.soundcheck.dev/fridge-fan",
    },
    {
        "part_id": "DISH-PUMP-812",
        "part_name": "Direct-Drive Drain Pump Assembly",
        "appliance_type": "Dishwasher",
        "sound_symptom": "Harsh grinding, clicking, or loud humming during drain phase with standing water",
        "defect_cause": "Broken impeller or foreign object (glass, bone, twist tie) jamming pump impeller",
        "oem_number": "WD19X25187",
        "price_usd": 38.50,
        "in_stock": True,
        "difficulty": "Intermediate (40 mins)",
        "tutorial_url": "https://tutorials.soundcheck.dev/dishwasher-drain-pump",
    },
    {
        "part_id": "HVAC-CAP-355",
        "part_name": "35/5 MFD 440V Dual Run Capacitor",
        "appliance_type": "HVAC / Air Conditioner",
        "sound_symptom": "Loud electrical humming or buzzing with outdoor condenser fan failing to spin",
        "defect_cause": "Degraded or bulged capacitor unable to phase-shift voltage to start the compressor/fan motor",
        "oem_number": "CAP-35-5-440",
        "price_usd": 18.25,
        "in_stock": True,
        "difficulty": "Advanced (Requires discharging high-voltage capacitor)",
        "tutorial_url": "https://tutorials.soundcheck.dev/hvac-run-capacitor",
    },
    {
        "part_id": "DRYER-ROLL-202",
        "part_name": "Drum Support Roller and Axle Kit",
        "appliance_type": "Clothes Dryer",
        "sound_symptom": "Rhythmic thumping, rumbling, or loud metal-on-metal squeaking as drum rotates",
        "defect_cause": "Worn sintered bronze bearing on support roller causing drum misalignment and friction",
        "oem_number": "349241T",
        "price_usd": 29.00,
        "in_stock": True,
        "difficulty": "Intermediate (50 mins)",
        "tutorial_url": "https://tutorials.soundcheck.dev/dryer-drum-rollers",
    },
    {
        "part_id": "MOW-BLADE-520",
        "part_name": "High-Lift Mower Blade & Spindle Bearing Kit",
        "appliance_type": "Lawnmower",
        "sound_symptom": "Violent vibration, shaking deck, and harsh rattling sound when mower blades engage",
        "defect_cause": "Bent blade out of balance or collapsed spindle ball bearing",
        "oem_number": "742-04053C",
        "price_usd": 34.50,
        "in_stock": True,
        "difficulty": "Intermediate (30 mins)",
        "tutorial_url": "https://tutorials.soundcheck.dev/mower-blade-spindle",
    },
]


def seed_database() -> None:
    print(f"Connecting to Firestore for project '{PROJECT_ID}'...")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection(COLLECTION_NAME)

    for item in SEEDED_PARTS:
        doc_ref = collection.document(item["part_id"])
        doc_ref.set(item)
        print(f"  ✓ Seeded part: {item['part_id']} - {item['part_name']}")

    print(f"\nSuccessfully seeded {len(SEEDED_PARTS)} parts into '{COLLECTION_NAME}' collection.")


if __name__ == "__main__":
    seed_database()
