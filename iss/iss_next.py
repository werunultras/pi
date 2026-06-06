#!/usr/bin/env python3
"""Show upcoming visible ISS passes for the configured observer location."""

from __future__ import annotations

import argparse
import math
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from skyfield.api import EarthSatellite, Loader, wgs84


LATITUDE = 51.454619
LONGITUDE = -0.306786
ALTITUDE_FT = 39
TIMEZONE = "Europe/London"
TLE_URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=tle"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show upcoming visible ISS passes for the Pi location."
    )
    parser.add_argument(
        "--days",
        type=int,
        default=45,
        help="How many days ahead to search. Default: 45.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="How many visible passes to show. Default: 5.",
    )
    parser.add_argument(
        "--min-elevation",
        type=float,
        default=10.0,
        help="Minimum pass elevation above horizon in degrees. Default: 10.",
    )
    parser.add_argument(
        "--cache-dir",
        default=str(Path.home() / ".cache" / "iss-tracker"),
        help="Directory used for TLE and ephemeris cache.",
    )
    parser.add_argument(
        "--refresh-hours",
        type=float,
        default=12.0,
        help="Refresh ISS TLE when cache is older than this. Default: 12.",
    )
    return parser.parse_args()


def refresh_tle(cache_dir: Path, max_age_hours: float) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / "iss.tle"

    if path.exists():
        age = datetime.now(timezone.utc) - datetime.fromtimestamp(
            path.stat().st_mtime, tz=timezone.utc
        )
        if age <= timedelta(hours=max_age_hours):
            return path

    with urllib.request.urlopen(TLE_URL, timeout=20) as response:
        body = response.read().decode("utf-8").strip()

    lines = [line.strip() for line in body.splitlines() if line.strip()]
    if len(lines) < 3 or not lines[1].startswith("1 ") or not lines[2].startswith("2 "):
        raise RuntimeError(f"unexpected TLE response from {TLE_URL!r}")

    path.write_text("\n".join(lines[:3]) + "\n", encoding="utf-8")
    return path


def load_satellite(tle_path: Path, timescale) -> EarthSatellite:
    lines = tle_path.read_text(encoding="utf-8").splitlines()
    return EarthSatellite(lines[1], lines[2], lines[0], timescale)


def direction_from_azimuth(degrees: float) -> str:
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
    index = int((degrees + 11.25) // 22.5) % 16
    return directions[index]


def format_local(dt_utc: datetime, tz: ZoneInfo) -> str:
    return dt_utc.astimezone(tz).strftime("%a %d %b %Y %H:%M:%S %Z")


def sample_times(start_utc: datetime, end_utc: datetime, step_seconds: int = 30):
    span = max(0, int((end_utc - start_utc).total_seconds()))
    count = max(1, math.ceil(span / step_seconds))
    return [start_utc + timedelta(seconds=i * span / count) for i in range(count + 1)]


def is_visible_pass(satellite, observer, eph, timescale, start_utc, end_utc) -> bool:
    earth = eph["earth"]
    sun = eph["sun"]

    for sample in sample_times(start_utc, end_utc):
        t = timescale.from_datetime(sample)
        alt, _, _ = (satellite - observer).at(t).altaz()
        if alt.degrees <= 0:
            continue

        sun_alt, _, _ = (earth + observer).at(t).observe(sun).apparent().altaz()
        if sun_alt.degrees > -6.0:
            continue

        if satellite.at(t).is_sunlit(eph):
            return True

    return False


def collect_visible_passes(args: argparse.Namespace):
    cache_dir = Path(args.cache_dir).expanduser()
    loader = Loader(str(cache_dir))
    timescale = loader.timescale()
    eph = loader("de421.bsp")
    tle_path = refresh_tle(cache_dir, args.refresh_hours)
    satellite = load_satellite(tle_path, timescale)
    observer = wgs84.latlon(
        LATITUDE,
        LONGITUDE,
        elevation_m=ALTITUDE_FT * 0.3048,
    )

    now = datetime.now(timezone.utc)
    t0 = timescale.from_datetime(now)
    t1 = timescale.from_datetime(now + timedelta(days=args.days))
    times, events = satellite.find_events(
        observer,
        t0,
        t1,
        altitude_degrees=args.min_elevation,
    )

    passes = []
    current = {}
    for t, event in zip(times, events):
        if event == 0:
            current = {"start": t}
        elif event == 1 and current:
            current["peak"] = t
        elif event == 2 and current and "peak" in current:
            current["end"] = t
            start_utc = current["start"].utc_datetime().replace(tzinfo=timezone.utc)
            peak_utc = current["peak"].utc_datetime().replace(tzinfo=timezone.utc)
            end_utc = current["end"].utc_datetime().replace(tzinfo=timezone.utc)

            if is_visible_pass(satellite, observer, eph, timescale, start_utc, end_utc):
                peak_alt, peak_az, _ = (satellite - observer).at(current["peak"]).altaz()
                start_alt, start_az, _ = (satellite - observer).at(current["start"]).altaz()
                end_alt, end_az, _ = (satellite - observer).at(current["end"]).altaz()
                passes.append(
                    {
                        "start": start_utc,
                        "peak": peak_utc,
                        "end": end_utc,
                        "duration": end_utc - start_utc,
                        "max_elevation": peak_alt.degrees,
                        "appears": direction_from_azimuth(start_az.degrees),
                        "peak_direction": direction_from_azimuth(peak_az.degrees),
                        "disappears": direction_from_azimuth(end_az.degrees),
                    }
                )
                if len(passes) >= args.count:
                    break
            current = {}

    return satellite.name, tle_path, passes


def main() -> int:
    args = parse_args()
    try:
        name, tle_path, passes = collect_visible_passes(args)
    except Exception as exc:
        print(f"iss-next: {exc}", file=sys.stderr)
        return 1

    tz = ZoneInfo(TIMEZONE)
    print(f"ISS visible passes from {LATITUDE:.6f}, {LONGITUDE:.6f} ({ALTITUDE_FT} ft)")
    print(f"TLE: {tle_path}")
    print(f"Satellite: {name}")
    print()

    if not passes:
        print(f"No visible passes found in the next {args.days} days.")
        return 0

    for index, item in enumerate(passes, start=1):
        duration_min = item["duration"].total_seconds() / 60.0
        print(f"{index}. {format_local(item['start'], tz)}")
        print(f"   Peak:       {format_local(item['peak'], tz)}")
        print(f"   Ends:       {format_local(item['end'], tz)}")
        print(f"   Duration:   {duration_min:.1f} min")
        print(f"   Max elev:   {item['max_elevation']:.0f} deg")
        print(
            "   Direction:  "
            f"appears {item['appears']}, peaks {item['peak_direction']}, "
            f"disappears {item['disappears']}"
        )
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
