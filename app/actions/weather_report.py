"""
Weather Report Action for JARVIS / Liseth.
Fetches real-time weather forecasts using Open-Meteo REST API (free, open, no API key required).
Provides fast, direct weather reports without forcing external browser popups,
with graceful offline fallback.
"""
import logging
from typing import Any, Dict, Optional
import httpx

logger = logging.getLogger("jarvis.weather")

# WMO Weather interpretation codes (WW) to friendly Spanish descriptions
WMO_WEATHER_CODES = {
    0: "cielo despejado y soleado",
    1: "cielo mayormente despejado",
    2: "parcialmente nublado",
    3: "cielo cubierto o nublado",
    45: "neblina",
    48: "niebla con escarcha",
    51: "llovizna ligera",
    53: "llovizna moderada",
    55: "llovizna densa",
    56: "llovizna helada ligera",
    57: "llovizna helada densa",
    61: "lluvia ligera",
    63: "lluvia moderada",
    65: "lluvia intensa",
    66: "lluvia helada ligera",
    67: "lluvia helada intensa",
    71: "nevada ligera",
    73: "nevada moderada",
    75: "nevada intensa",
    77: "granos de nieve",
    80: "chubascos dispersos",
    81: "chubascos moderados",
    82: "chubascos violentos",
    85: "chubascos de nieve ligeros",
    86: "chubascos de nieve intensos",
    95: "tormenta eléctrica",
    96: "tormenta eléctrica con granizo ligero",
    99: "tormenta eléctrica con granizo fuerte",
}

# Default location: Bogotá, Colombia (Lat: 4.7110, Lon: -74.0721)
DEFAULT_CITY = "Bogotá"
DEFAULT_LAT = 4.7110
DEFAULT_LON = -74.0721


def get_city_coordinates(city_name: str) -> Optional[tuple[float, float, str]]:
    """Resolves city coordinates via Open-Meteo Geocoding API."""
    if not city_name or city_name.strip().lower() in ["bogota", "bogotá", "aquí", "aqui", "mi ciudad", "local"]:
        return (DEFAULT_LAT, DEFAULT_LON, DEFAULT_CITY)

    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": city_name.strip(), "count": 1, "language": "es", "format": "json"}
        with httpx.Client(timeout=4.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results")
                if results and len(results) > 0:
                    first = results[0]
                    name = first.get("name", city_name)
                    country = first.get("country", "")
                    label = f"{name}, {country}" if country else name
                    return (first["latitude"], first["longitude"], label)
    except Exception as e:
        logger.debug(f"[Weather] Error en geocoding para {city_name}: {e}")

    return None


def fetch_weather_report(city: str = DEFAULT_CITY) -> Dict[str, Any]:
    """
    Fetches real-time weather data from Open-Meteo.
    Returns structured dictionary with condition, temperature, humidity, rain chance, and text summary.
    """
    coords = get_city_coordinates(city)
    lat, lon, city_label = coords if coords else (DEFAULT_LAT, DEFAULT_LON, city or DEFAULT_CITY)

    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto",
        }

        with httpx.Client(timeout=httpx.Timeout(2.5, connect=1.5)) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current", {})
                daily = data.get("daily", {})

                temp = current.get("temperature_2m")
                feels_like = current.get("apparent_temperature", temp)
                humidity = current.get("relative_humidity_2m")
                code = current.get("weather_code", 0)
                wind = current.get("wind_speed_10m", 0)
                condition = WMO_WEATHER_CODES.get(code, "tiempo estable")

                # Daily forecast
                rain_prob = 0
                temp_max = None
                temp_min = None
                if daily.get("precipitation_probability_max"):
                    rain_prob = daily["precipitation_probability_max"][0]
                if daily.get("temperature_2m_max"):
                    temp_max = daily["temperature_2m_max"][0]
                if daily.get("temperature_2m_min"):
                    temp_min = daily["temperature_2m_min"][0]

                # Compose natural text summary
                parts = [f"En {city_label} tenemos actualmente {temp:.0f}°C"]
                if feels_like and abs(feels_like - temp) >= 2:
                    parts.append(f"(sensación de {feels_like:.0f}°C)")
                parts.append(f"con {condition}.")

                extra = []
                if humidity:
                    extra.append(f"humedad al {humidity}%")
                if rain_prob > 0:
                    extra.append(f"probabilidad de lluvia del {rain_prob}%")
                elif wind > 20:
                    extra.append(f"vientos de {wind:.0f} km/h")

                if extra:
                    parts.append(f"Se registra {', y '.join(extra)}.")

                summary = " ".join(parts)
                return {
                    "ok": True,
                    "city": city_label,
                    "temperature": temp,
                    "feels_like": feels_like,
                    "condition": condition,
                    "humidity": humidity,
                    "rain_probability": rain_prob,
                    "temp_max": temp_max,
                    "temp_min": temp_min,
                    "summary": summary,
                }

    except Exception as e:
        logger.warning(f"[Weather] Error consultando Open-Meteo: {e}")

    # Graceful fallback
    return {
        "ok": False,
        "city": city or DEFAULT_CITY,
        "temperature": 18.0,
        "condition": "tiempo templado",
        "summary": f"Actualmente no fue posible conectar con el satélite meteorológico para {city or DEFAULT_CITY}. El clima promedio se estima templado.",
    }


def weather_action(
    parameters: dict,
    player=None,
    session_memory=None,
) -> str:
    """Action entry point for Gemini and dispatcher."""
    city = (parameters.get("city") or DEFAULT_CITY).strip()
    data = fetch_weather_report(city)
    msg = data.get("summary", f"El clima en {city} se encuentra templado, señor Santiago.")

    if player:
        try:
            player.write_log(f"[Weather] {msg}")
        except Exception:
            pass

    return msg


# Tool declaration auto-discovered by ActionDispatcher
TOOL = {
    "name": "weather_report",
    "description": "Obtiene el reporte del clima en tiempo real (temperatura, lluvia, pronóstico) para cualquier ciudad o la ubicación actual.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "city": {
                "type": "STRING",
                "description": "Nombre de la ciudad (por defecto Bogotá)"
            }
        },
        "required": []
    },
    "handler": weather_action,
}
