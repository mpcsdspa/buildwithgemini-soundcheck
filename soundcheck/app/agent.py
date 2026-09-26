# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


MODEL = "gemini-2.5-flash"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


import json
from pathlib import Path
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from app.energy_service import get_appliance_energy_cost
from app.firestore_service import (
    add_part_to_catalog,
    get_part_details,
    search_parts_catalog,
    update_part_inventory,
)
from app.image_service import generate_component_diagram
from app.maps_service import geocode_address, search_nearby_places
from app.roi_calculator import calculate_repair_vs_replace_roi

# Load sandbox resource name from deployment_metadata.json with fallback to created sandbox
SANDBOX_RESOURCE_NAME = "projects/464605011101/locations/us-east1/reasoningEngines/9124633693657235456/sandboxEnvironments/8125179823032107008"
_metadata_file = Path(__file__).resolve().parent.parent / "deployment_metadata.json"
if _metadata_file.exists():
    try:
        _meta = json.loads(_metadata_file.read_text())
        SANDBOX_RESOURCE_NAME = _meta.get("sandbox_resource_name") or SANDBOX_RESOURCE_NAME
    except Exception:
        pass

sandbox_executor = AgentEngineSandboxCodeExecutor(sandbox_resource_name=SANDBOX_RESOURCE_NAME)


from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

# WRITE: after each turn, send the session to Memory Bank for extraction.
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from app.a2ui_utils import a2ui_callback

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are SoundCheck, an acoustic diagnostic and repair assistant for home appliances and tools. "
        "You help homeowners and DIYers identify mechanical and electrical issues based on sound symptoms, "
        "search the Firestore parts catalog for OEM replacement parts, look up repair difficulty and tutorial guides, "
        "calculate repair vs. replace ROI to provide financial recommendations, "
        "fetch real appliance energy running costs by state, "
        "find nearby hardware and supply stores using Google Maps Geocoding and Places API, "
        "generate technical exploded diagrams and schematics for parts and appliances, "
        "safely execute Python code in the Agent Engine sandbox for complex calculations or acoustic signal analysis (always write clean, executable Python code with print() statements and without REPL prompts), "
        "remember the user's stated allergies, health/chemical sensitivities, appliance preferences, past repairs, and equipment details from previous conversations to personalize advice, safety warnings, and diagnostics, "
        "and record or update parts in the catalog."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=sandbox_executor,
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
    tools=[
        PreloadMemoryTool(),
        search_parts_catalog,
        get_part_details,
        add_part_to_catalog,
        update_part_inventory,
        calculate_repair_vs_replace_roi,
        get_appliance_energy_cost,
        geocode_address,
        search_nearby_places,
        generate_component_diagram,
        get_weather,
        get_current_time,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
