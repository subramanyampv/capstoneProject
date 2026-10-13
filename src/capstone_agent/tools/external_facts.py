"""Allowlisted read-only public facts for the ETA demo; no arbitrary URLs or writes."""

import json
import math
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener

from capstone_agent.model_client import NoRedirect


class FactToolError(ValueError):
    pass


def get_json(url):
    request = Request(url, headers={"Accept": "application/json",
        "User-Agent": "capstone-agent/0.1 (synthetic demo; github.com/subramanyampv/capstoneProject)"})
    try:
        with build_opener(NoRedirect()).open(request, timeout=6) as response:
            body = response.read(1_000_001)
        if len(body) > 1_000_000:
            raise FactToolError("Fact response exceeded size limit.")
        return json.loads(body)
    except (HTTPError, URLError, OSError, ValueError):
        raise FactToolError("External fact source unavailable or invalid; no estimate inferred.") from None


def point(latitude, longitude):
    if (type(latitude) not in {int, float} or type(longitude) not in {int, float}
            or not math.isfinite(latitude) or not math.isfinite(longitude)
            or not -90 <= latitude <= 90 or not -180 <= longitude <= 180):
        raise FactToolError("Invalid latitude/longitude.")
    return round(latitude, 4), round(longitude, 4)


def route_distance(origin_lat, origin_lon, destination_lat, destination_lon, *, fetch=get_json):
    origin_lat, origin_lon = point(origin_lat, origin_lon)
    destination_lat, destination_lon = point(destination_lat, destination_lon)
    url = ("https://router.project-osrm.org/route/v1/driving/"
           f"{origin_lon},{origin_lat};{destination_lon},{destination_lat}?overview=false&skip_waypoints=true")
    payload = fetch(url)
    try:
        if payload["code"] != "Ok":
            raise ValueError
        meters = payload["routes"][0]["distance"]
        if type(meters) not in {int, float} or not math.isfinite(meters) or meters < 0:
            raise ValueError
        miles = meters / 1609.344
        if miles > 25000:
            raise ValueError
        return {"distance_miles": round(miles, 2), "source": "OSRM public driving-route demo",
                "source_url": "https://router.project-osrm.org", "route_type": "road-distance proxy"}
    except (KeyError, IndexError, TypeError, ValueError):
        raise FactToolError("No validated route distance returned.") from None


def weather_alerts(latitude, longitude, *, fetch=get_json):
    latitude, longitude = point(latitude, longitude)
    if not 24 <= latitude <= 50 or not -125 <= longitude <= -66:
        raise FactToolError("ETA weather demo currently supports contiguous US destinations only.")
    payload = fetch(f"https://api.weather.gov/alerts/active?point={latitude},{longitude}")
    try:
        features = payload["features"]
        if not isinstance(features, list):
            raise ValueError
        events = [feature["properties"]["event"] for feature in features]
        if not all(isinstance(event, str) and len(event) <= 200 for event in events):
            raise ValueError
        snow = any(any(term in event.lower() for term in ("snow", "blizzard", "winter storm", "winter weather")) for event in events)
        storm = any(any(term in event.lower() for term in ("storm", "hurricane", "tornado")) for event in events)
        condition = "storm_and_snow" if snow and storm else "snow" if snow else "storm" if storm else "unknown" if events else "no_disruption_alert"
        return {"weather": condition, "alert_count": len(events), "source": "NWS active destination-area alerts",
                "source_url": "https://api.weather.gov", "limits": "Destination alerts only, not route-wide or arrival-day forecast."}
    except (KeyError, IndexError, TypeError, ValueError):
        raise FactToolError("No validated weather-alert result returned.") from None
