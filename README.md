# Raspberry Pi

Operational notes and helper scripts for the home Raspberry Pi.

## Access

Use NordVPN Meshnet as the primary access path:

```bash
ssh pi-mesh
```

Meshnet identity:

```text
Hostname: francesco.dicostanzo-andes.nord
Meshnet IP: 100.100.117.13
```

LAN fallback when at home:

```bash
ssh pi-ubuntu
```

## What Runs Here

- Flightradar24 ADS-B feeder using the Nooelec RTL-SDR and 978/1090 MHz antenna.
- On-demand ISS visible-pass checker.
- On-demand weather checker for the configured location.
- NordVPN Meshnet for remote access.

## Common Commands

Check FR24:

```bash
ssh pi-mesh fr24feed-status
```

Check upcoming visible ISS passes:

```bash
ssh pi-mesh iss-next
```

Check local weather:

```bash
ssh pi-mesh weather-now
```

Check system status:

```bash
ssh pi-mesh 'uptime; systemctl is-active fr24feed; nordvpn settings | grep Meshnet'
```

## Documentation

- [SETUP.md](SETUP.md): base Pi setup, SSH, Meshnet, hardware, and verification commands.
- [flightradar/FLIGHTRADAR.md](flightradar/FLIGHTRADAR.md): FR24 feeder setup and troubleshooting notes.
- [iss/ISS.md](iss/ISS.md): ISS visible-pass checker setup and usage.
- [weather/WEATHER.md](weather/WEATHER.md): weather checker setup and usage.

## Scripts

- [iss/iss_next.py](iss/iss_next.py): computes visible ISS passes.
- [iss/iss-next](iss/iss-next): Pi wrapper for `iss-next`.
- [weather/weather_now.py](weather/weather_now.py): fetches and formats weather from Open-Meteo.
- [weather/weather-now](weather/weather-now): Pi wrapper for `weather-now`.

## Notes

Secrets are intentionally not documented in this repo. This includes the Pi password, NordVPN token, and FR24 sharing key.
