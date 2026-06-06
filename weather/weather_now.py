#!/usr/bin/env python3
"""Show on-demand weather for the configured Pi location."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


LATITUDE = 51.454619
LONGITUDE = -0.306786
ALTITUDE_FT = 39
TIMEZONE = "Europe/London"
API_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show current and near-term weather for the Pi location."
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=6,
        help="How many upcoming hourly forecast rows to show. Default: 6.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the raw cached/fetched API payload as JSON.",
    )
    parser.add_argument(
        "--cache-dir",
        default=str(Path.home() / ".cache" / "weather"),
        help="Directory used for weather cache.",
    )
    return parser.parse_args()


def build_url() -> str:
    params = {
        "latitude": f"{LATITUDE:.6f}",
        "longitude": f"{LONGITUDE:.6f}",
        "current": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation",
                "rain",
                "weather_code",
                "cloud_cover",
                "pressure_msl",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
            ]
        ),
        "hourly": ",".join(
            [
                "temperature_2m",
                "precipitation_probability",
                "rain",
                "weather_code",
                "cloud_cover",
                "wind_speed_10m",
                "wind_gusts_10m",
                "wind_direction_10m",
                "visibility",
            ]
        ),
        "timezone": TIMEZONE,
        "forecast_days": "2",
    }
    return f"{API_URL}?{urllib.parse.urlencode(params)}"


def cache_path(cache_dir: str) -> Path:
    path = Path(cache_dir).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path / "weather.json"


def fetch_weather(url: str, path: Path) -> tuple[dict, bool, str | None]:
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            data = json.load(response)
        envelope = {
            "fetched_at": datetime.now(ZoneInfo(TIMEZONE)).isoformat(timespec="seconds"),
            "url": url,
            "data": data,
        }
        path.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
        return envelope, False, None
    except Exception as exc:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8")), True, str(exc)
        raise RuntimeError(f"could not fetch weather and no cache exists: {exc}") from exc


def weather_text(code: int | None) -> str:
    if code is None:
        return "Unknown"
    return WEATHER_CODES.get(code, f"Weather code {code}")


def value(data: dict, units: dict, key: str, suffix: str = "") -> str:
    item = data.get(key)
    unit = units.get(key, suffix)
    if item is None:
        return "n/a"
    return f"{item}{unit}"


def wind_direction(degrees: float | int | None) -> str:
    if degrees is None:
        return "n/a"
    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    index = int((float(degrees) + 11.25) // 22.5) % 16
    return f"{directions[index]} ({degrees}°)"


def print_report(envelope: dict, cache_used: bool, fetch_error: str | None, hours: int) -> None:
    data = envelope["data"]
    current = data.get("current", {})
    current_units = data.get("current_units", {})
    hourly = data.get("hourly", {})
    hourly_units = data.get("hourly_units", {})

    print(f"Weather for {LATITUDE:.6f}, {LONGITUDE:.6f} ({ALTITUDE_FT} ft)")
    print(f"Timezone: {data.get('timezone', TIMEZONE)}")
    print(f"Fetched: {envelope.get('fetched_at', 'unknown')}")
    if cache_used:
        print(f"Source: cached data; refresh failed: {fetch_error}")
    else:
        print("Source: Open-Meteo")
    print()

    code = current.get("weather_code")
    print(f"Current at {current.get('time', 'unknown')}")
    print(f"  Conditions:     {weather_text(code)}")
    print(f"  Temperature:    {value(current, current_units, 'temperature_2m')}")
    print(f"  Feels like:     {value(current, current_units, 'apparent_temperature')}")
    print(f"  Humidity:       {value(current, current_units, 'relative_humidity_2m')}")
    print(f"  Rain:           {value(current, current_units, 'rain')}")
    print(f"  Precipitation:  {value(current, current_units, 'precipitation')}")
    print(f"  Cloud cover:    {value(current, current_units, 'cloud_cover')}")
    print(f"  Pressure:       {value(current, current_units, 'pressure_msl')}")
    print(
        "  Wind:           "
        f"{value(current, current_units, 'wind_speed_10m')} "
        f"{wind_direction(current.get('wind_direction_10m'))}, "
        f"gusts {value(current, current_units, 'wind_gusts_10m')}"
    )

    times = hourly.get("time", [])
    start_index = next_hour_index(times, current.get("time"))
    count = max(0, min(hours, len(times) - start_index))
    if count:
        print()
        print(f"Next {count} hours")
        for offset in range(count):
            index = start_index + offset
            item = {key: hourly.get(key, [None] * len(times))[index] for key in hourly}
            print(
                f"  {times[index]}: "
                f"{item.get('temperature_2m')}{hourly_units.get('temperature_2m', '')}, "
                f"{weather_text(item.get('weather_code'))}, "
                f"rain {item.get('rain')}{hourly_units.get('rain', '')}, "
                f"precip {item.get('precipitation_probability')}"
                f"{hourly_units.get('precipitation_probability', '')}, "
                f"cloud {item.get('cloud_cover')}{hourly_units.get('cloud_cover', '')}, "
                f"wind {item.get('wind_speed_10m')}{hourly_units.get('wind_speed_10m', '')} "
                f"{wind_direction(item.get('wind_direction_10m'))}"
            )


def next_hour_index(times: list[str], current_time: str | None) -> int:
    if not current_time:
        return 0
    try:
        current = datetime.fromisoformat(current_time)
    except ValueError:
        return 0

    for index, item in enumerate(times):
        try:
            if datetime.fromisoformat(item) >= current:
                return index
        except ValueError:
            continue
    return len(times)


def main() -> int:
    args = parse_args()
    try:
        path = cache_path(args.cache_dir)
        envelope, cache_used, fetch_error = fetch_weather(build_url(), path)
    except Exception as exc:
        print(f"weather-now: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(envelope["data"], indent=2))
        return 0

    print_report(envelope, cache_used, fetch_error, args.hours)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
