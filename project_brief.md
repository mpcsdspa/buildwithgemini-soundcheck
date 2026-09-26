# My agent: SoundCheck

One-liner: A conversational agent that helps homeowners and DIYers diagnose malfunctioning home appliances and tools from audio clips with a catalog of replacement parts, diagnostic guides, and repair tutorials.

Tool coverage:
- Memory: User's household appliance & tool inventory (brand, model, age), past diagnosis history, maintenance logs, and DIY skill level.
- Tools: Replacement part lookup (OEM part numbers, pricing, availability), repair video/guide search, and acoustic diagnostic rule lookup.
- Catalog/UI: Diagnostic report cards (issue, severity, confidence, symptoms), replacement parts table (part name, number, cost, links), and step-by-step repair walkthrough cards.
- Image gen: Exploded diagram / schematic illustrations highlighting where the faulty component is located inside the appliance.
- Sandbox: Audio frequency/FFT computation and repair cost vs. appliance replacement ROI calculator.

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): Code sandbox for audio frequency/FFT analysis and repair vs. replace ROI calculations, multimodal audio ingestion with Gemini, Cloud Trace.
