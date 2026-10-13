> Historical document. Superseded by [Architecture and Plan v3](../../architecture_and_plan.md). Not an active requirement.

# Read-only tool candidates

| Service | Tool use | Status and boundaries |
|---|---|---|
| [OSRM](https://project-osrm.org/docs/v5.24.0/api/) | driving-route distance from city-centre coordinates | Allowlisted ETA fact adapter implemented; public demo service is not a production SLA or carrier route. |
| [National Weather Service](https://www.weather.gov/documentation/services-web-api) | active storm/snow alerts at a destination | Allowlisted adapter implemented for contiguous US demo; public data API, not an open-source retailer system. Absence of alerts is not a clear-weather forecast. |
| [DummyJSON products](https://dummyjson.com/docs/products) | synthetic external product lookup | Recommended optional demo source; never silently replace the frozen local catalog or accept its returnPolicy as retailer authority. |
| [Mockoon](https://mockoon.com/cli/) | locally hosted mock orders/tracking/timeouts | Recommended self-hosted open-source mock API service for Phase 5 tests. No external customer systems required. |
| [Medusa Store API](https://docs.medusajs.com/api/store/) | self-hosted commerce catalog and order integration | Later production-like integration candidate; requires deployment, publishable keys and proper customer authorization. Not connected. |

External facts are data, not instructions or permission. APIs are allowlisted reads
with bounded timeouts, response-size limits and validated outputs. The UI sends
only submitted city-centre coordinates, never account IDs, API keys, prompts or full
street addresses to OSRM/NWS. No API call happens from opening the UI.

ETA calculation uses the separate, versioned synthetic `delivery_estimate_rules.json`:
minimum 1 day, ceil(miles × 3 / 1000), storm/snow adds 2 days once, upper buffer 2 days.
Missing or stale facts produce uncertainty. Active destination alerts are neither a
route-wide forecast nor arrival-day weather; the output remains an estimate.
