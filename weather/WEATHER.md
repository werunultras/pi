# Weather Checker

Setup date: 2026-06-05

## Summary

The Pi has an on-demand command for checking weather at the same location used by Flightradar24 and ISS pass prediction. It does not create alerts, background services, cron jobs, or SDR activity.

Run:

```bash
ssh pi weather-now
```

## Location

```text
Latitude: 51.454619
Longitude: -0.306786
Altitude: 39 ft
Timezone: Europe/London
```

## Implementation

The script is stored in this repo as:

```text
weather/weather_now.py
```

It is installed on the Pi as:

```text
/home/pi/.local/share/weather/weather_now.py
/home/pi/bin/weather-now
/usr/local/bin/weather-now
```

It uses Open-Meteo and does not need an API key:

```text
https://api.open-meteo.com/v1/forecast
```

It caches the last successful response in:

```text
/home/pi/.cache/weather/weather.json
```

If Open-Meteo is temporarily unavailable, `weather-now` uses the cached data and prints the fetch error.

## Usage

Current weather plus the next 6 hourly rows:

```bash
weather-now
```

More hours:

```bash
weather-now --hours 12
```

Raw API payload:

```bash
weather-now --json
```

Example verified output:

```text
Current at 2026-06-05T21:30
  Conditions:     Overcast
  Temperature:    14.4°C
  Feels like:     11.5°C
  Humidity:       59%

Next 6 hours
  2026-06-05T22:00: 14.1°C, Overcast, rain 0.0mm, precip 0%, cloud 100%, wind 12.6km/h S (186°)
```

## Notes

- This is on-demand only.
- It does not interact with the SDR.
- Flightradar24 remains the always-on SDR service.
