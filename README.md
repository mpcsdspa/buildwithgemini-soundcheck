# 🔊 SoundCheck · Diagnostic & Repair Assistant

> Built during the **Build with Gemini World Tour** (Track 3: Agent-First Applications)

**SoundCheck** is an intelligent acoustic diagnostic and repair assistant designed for homeowners and DIYers. It identifies mechanical and electrical appliance malfunctions from sound symptoms and audio descriptions, checks OEM replacement parts, calculates repair vs. replace ROI, looks up energy consumption costs, locates local supply stores, generates exploded component diagrams, and safely executes calculations in a sandboxed Python environment.

---

## ✨ Features & Architecture

| Feature | Powered By | Description |
|---|---|---|
| 🤖 **Agent Reasoning Loop** | Google ADK & Gemini 3.6 Flash | Orchestrates multi-step diagnostics, tool dispatch, and user advice. |
| 🧠 **Persistent Long-Term Memory** | Vertex AI Memory Bank | Remembers user appliance inventories, past repairs, and user allergies/chemical sensitivities across sessions. |
| 🗄️ **Parts Catalog & Inventory** | Google Cloud Firestore | Real-time querying and updating of OEM parts, pricing, and stock status. |
| 📊 **Financial Decision Engine** | Custom ROI Analysis Tool | Evaluates appliance age, repair expense vs. new appliance purchase, and payback period. |
| ⚡ **Live Energy Cost Estimation** | OpenEI Public Utility API | Retrieves state-by-state electricity rates and annual operating cost estimates. |
| 📍 **Hardware Store Locator** | Google Maps Geocoding & Places (New) API | Resolves coordinates and finds nearby repair and hardware supply retailers. |
| 🎨 **Exploded Component Schematics** | `gemini-3.1-flash-lite-image` + Google Cloud Storage | Generates technical diagrams and uploads them to public Cloud Storage. |
| 🧪 **Code Sandbox Execution** | Agent Engine Sandbox Environments | Safely executes Python code for acoustic calculations and mathematical modeling. |
| 🪟 **Agent-First UI (A2UI)** | A2UI v0.8 (`a2ui-agent-sdk`) | Emits rich structured display cards and component layouts directly in the ADK web interface. |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) package manager
- Google Cloud SDK (`gcloud`) authenticated with your project

### Installation

```bash
cd soundcheck
uv sync
```

### Local Development

Launch the ADK Web playground with memory service enabled:

```bash
uv run adk web . --port 8080 --reload_agents --memory_service_uri=agentengine://<AGENT_ENGINE_ID>
```

Open `http://localhost:8080` in your browser. (Note: Turn off token streaming in the dev UI settings to view rendered A2UI cards).

---

## 📂 Project Structure

```
.
├── project_brief.md              # Original project brief and tool coverage checklist
├── soundcheck/
│   ├── app/
│   │   ├── agent.py              # Root agent definition, system prompts, callbacks & tools
│   │   ├── a2ui_utils.py         # A2UI response formatting callback
│   │   ├── firestore_service.py  # Firestore OEM catalog service
│   │   ├── energy_service.py     # OpenEI electricity rate lookup
│   │   ├── maps_service.py       # Google Maps Geocoding & Places API client
│   │   ├── image_service.py      # Diagram generation via Gemini Flash-Lite-Image
│   │   ├── roi_calculator.py     # Repair vs. replace financial engine
│   │   ├── fast_api_app.py       # FastAPI server with A2A protocol support
│   │   └── app_utils/            # Service injection and A2A route helpers
│   ├── tests/                    # Unit and integration tests
│   ├── Dockerfile                # Container deployment spec
│   ├── deployment_metadata.json  # Agent Engine and Sandbox environment references
│   └── pyproject.toml            # Dependencies and build configuration
```
