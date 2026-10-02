# ISS Visible Pass Checker

Setup date: 2026-06-05

## Summary

The Pi has an on-demand command for checking upcoming visible ISS passes. It does not create alerts, background services, cron jobs, or SDR activity.

Run:

```bash
ssh pi
iss-next
```

or from the Mac:

```bash
ssh pi iss-next
```

## Location

The checker uses the same location configured for Flightradar24:

```text
Latitude: 51.454619
Longitude: -0.306786
Altitude: 39 ft
Timezone: Europe/London
```

## Implementation

The script is stored in this repo as:

```text
iss/iss_next.py
```

It is installed on the Pi as:

```text
/home/pi/bin/iss-next
```

It is also symlinked into the normal command path:

```text
/usr/local/bin/iss-next
```

It uses a local virtualenv:

```text
/home/pi/.local/share/iss-tracker/venv
```

It caches current ISS TLE data and Skyfield ephemeris files in:

```text
/home/pi/.cache/iss-tracker/
```

Data source:

```text
https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=tle
```

## Output

`iss-next` prints the next visible ISS passes in UK local time, including:

- Start time
- Peak time
- End time
- Duration
- Maximum elevation
- Appears / peaks / disappears direction

Useful options:

```bash
iss-next --count 10
iss-next --days 14
iss-next --min-elevation 20
```

The default search window is 45 days because visible ISS passes can be clustered; there may be no visible passes in a shorter 7-10 day window.

Example verified output:

```text
1. Wed 24 Jun 2026 03:17:57 BST
   Peak:       Wed 24 Jun 2026 03:20:14 BST
   Ends:       Wed 24 Jun 2026 03:22:31 BST
   Duration:   4.6 min
   Max elev:   17 deg
   Direction:  appears S, peaks SE, disappears E
```

## Notes

- This is visibility prediction only; it does not use the SDR.
- Flightradar24 remains the always-on SDR service.
- Visible passes require the observer location to be dark enough and the ISS to be sunlit, so there may be fewer visible passes than overhead orbital passes.
