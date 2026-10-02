# Raspberry Pi

Operational notes and helper scripts for the home Raspberry Pi.

## Access

Use Tailscale as the primary access path. Connect this Mac to Tailscale, then run:

```bash
ssh pi
```

Tailscale address: `100.75.237.100` (SSH user `pi`, port `22`).

In Termius, open the saved **Pi** host. It uses the **Pi — Tailscale** SSH key in the Personal vault. The connection was verified on 2026-10-02.

LAN fallback when at home:

```bash
ssh pi-ubuntu
```

## What Runs Here

- Flightradar24 ADS-B feeder using the Nooelec RTL-SDR and 978/1090 MHz antenna.
- On-demand ISS visible-pass checker.
- On-demand weather checker for the configured location.
- Tailscale for remote access.

## Common Commands

Check FR24:

```bash
ssh pi fr24feed-status
```

Check upcoming visible ISS passes:

```bash
ssh pi iss-next
```

Check local weather:

```bash
ssh pi weather-now
```

Check system status:

```bash
ssh pi 'uptime; systemctl is-active fr24feed; tailscale ip -4'
```

## Documentation

- [SETUP.md](SETUP.md): base Pi setup, Tailscale, SSH, Termius, hardware, and verification commands.
- [flightradar/FLIGHTRADAR.md](flightradar/FLIGHTRADAR.md): FR24 feeder setup and troubleshooting notes.
- [iss/ISS.md](iss/ISS.md): ISS visible-pass checker setup and usage.
- [weather/WEATHER.md](weather/WEATHER.md): weather checker setup and usage.

## Scripts

- [iss/iss_next.py](iss/iss_next.py): computes visible ISS passes.
- [iss/iss-next](iss/iss-next): Pi wrapper for `iss-next`.
- [weather/weather_now.py](weather/weather_now.py): fetches and formats weather from Open-Meteo.
- [weather/weather-now](weather/weather-now): Pi wrapper for `weather-now`.

## Notes

Secrets are intentionally not documented in this repo. This includes private SSH keys, the Pi password, VPN tokens, and the FR24 sharing key.
