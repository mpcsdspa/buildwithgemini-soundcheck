"""Google Maps Geocoding and Places (New) API service."""

import os
from typing import Any, Dict, List
import requests

GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
PLACES_NEARBY_URL = "https://places.googleapis.com/v1/places:searchNearby"


def get_maps_api_key() -> str:
    """Retrieve Google Maps API Key from environment variable."""
    return os.getenv("GOOGLE_MAPS_API_KEY", "").strip()


def geocode_address(address: str) -> Dict[str, Any]:
    """Geocode a physical address or city into latitude and longitude coordinates using Google Maps Geocoding API.

    Args:
        address: The street address, city, or postal code to geocode (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'Austin, TX').

    Returns:
        A dictionary with the formatted address, latitude, and longitude.
    """
    api_key = get_maps_api_key()
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY is not set in the environment or .env file."}

    try:
        resp = requests.get(
            GEOCODING_URL,
            params={"address": address, "key": api_key},
            timeout=8,
        )
        data = resp.json()

        if data.get("status") != "OK" or not data.get("results"):
            return {
                "error": f"Geocoding failed with status: {data.get('status')}",
                "error_message": data.get("error_message", "No results found."),
            }

        first_result = data["results"][0]
        location = first_result.get("geometry", {}).get("location", {})

        return {
            "address": first_result.get("formatted_address"),
            "location": {
                "latitude": location.get("lat"),
                "longitude": location.get("lng"),
            },
        }
    except Exception as e:
        return {"error": f"Failed to execute geocoding request: {e}"}


def search_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "hardware_store",
    radius_meters: float = 5000.0,
) -> List[Dict[str, Any]]:
    """Search for nearby places of a given type (e.g., hardware stores, home goods stores) using Places API (New).

    Args:
        latitude: Latitude coordinate of the search center.
        longitude: Longitude coordinate of the search center.
        place_type: Place type to search for (e.g., 'hardware_store', 'home_goods_store', 'department_store').
        radius_meters: Search radius in meters (default is 5000 meters / 5 km).

    Returns:
        A list of nearby places with their name, formatted address, and location.
    """
    api_key = get_maps_api_key()
    if not api_key:
        return [{"error": "GOOGLE_MAPS_API_KEY is not set in the environment or .env file."}]

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
    }

    payload = {
        "includedTypes": [place_type],
        "maxResultCount": 10,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                },
                "radius": float(radius_meters),
            }
        },
    }

    try:
        resp = requests.post(PLACES_NEARBY_URL, json=payload, headers=headers, timeout=8)
        data = resp.json()

        if resp.status_code != 200:
            return [{"error": f"Places API returned status {resp.status_code}: {data}"}]

        places = data.get("places", [])
        results = []
        for p in places:
            display_name = p.get("displayName", {}).get("text", "")
            address = p.get("formattedAddress", "")
            loc = p.get("location", {})
            results.append({
                "name": display_name,
                "address": address,
                "location": {
                    "latitude": loc.get("latitude"),
                    "longitude": loc.get("longitude"),
                },
            })

        return results
    except Exception as e:
        return [{"error": f"Failed to execute Places API request: {e}"}]
