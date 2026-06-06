# Raspberry Pi Setup

Setup date: 2026-06-05

## Device

- Hostname: `pi`
- User: `pi`
- OS: Ubuntu 24.04.4 LTS
- Architecture: `aarch64`
- Current kernel after upgrade/reboot: `6.8.0-1057-raspi`

## Connected Hardware

- Nooelec RTL-SDR v5 SDR, NESDR SMArt HF/VHF/UHF, RTL2832U and R820T2/R860 based.
- Bingfu dual-band 978 MHz / 1090 MHz 7 dBi magnetic base antenna.

Ubuntu detects the SDR as:

```text
Bus 004 Device 002: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T
```

## Network

The Pi should be reached through NordVPN Meshnet going forward.

Primary SSH command from this Mac:

```bash
ssh pi-mesh
```

Meshnet identity:

```text
Hostname: francesco.dicostanzo-andes.nord
Meshnet IP: 100.100.117.13
```

The original home LAN address is still useful as a fallback when on the same network:

```text
192.168.1.193
```

LAN fallback SSH command from this Mac:

```bash
ssh pi-ubuntu
```

Do not rely on the LAN IP for normal access from outside the home. Use `pi-mesh`.

## SSH Setup

Passwordless SSH was configured from this Mac.

Local private key:

```text
/Users/francesco/.ssh/codex/pi-ubuntu
```

The corresponding public key was added to:

```text
/home/pi/.ssh/authorized_keys
```

The Mac SSH config was updated at:

```text
/Users/francesco/.ssh/config
```

Current aliases:

```sshconfig
Host pi-mesh
  HostName 100.100.117.13
  User pi
  IdentityFile /Users/francesco/.ssh/codex/pi-ubuntu
  IdentitiesOnly yes

Host pi-ubuntu
  HostName 192.168.1.193
  User pi
  IdentityFile /Users/francesco/.ssh/codex/pi-ubuntu
  IdentitiesOnly yes
```

`pi-mesh` was added after verifying the Pi was reachable over Meshnet. The Meshnet host key for `100.100.117.13` was accepted into this Mac's `known_hosts`.

Use:

```bash
ssh pi-mesh
```

instead of:

```bash
ssh pi-ubuntu
```

unless Meshnet is unavailable and the Mac is on the home LAN.

## System Updates

The Pi was updated immediately after setup:

```bash
sudo apt update
sudo apt -y upgrade
sudo reboot
```

After reboot, the Pi came back online and no reboot was required.

## NordVPN And Meshnet

NordVPN was installed using the official Linux CLI installer:

```bash
sh <(curl -sSf https://downloads.nordcdn.com/apps/linux/install.sh)
```

Installed version:

```text
NordVPN Version 5.0.0
```

The installer added user `pi` to the `nordvpn` group.

The NordVPN daemon is enabled and active:

```bash
systemctl is-enabled nordvpnd
systemctl is-active nordvpnd
```

Expected output:

```text
enabled
active
```

Meshnet was enabled after login:

```bash
nordvpn set meshnet on
```

Current important NordVPN settings:

```text
Technology: NORDLYNX
Firewall: enabled
User Consent: disabled
Auto-connect: disabled
Meshnet: enabled
```

The VPN tunnel itself is not connected, which is fine for Meshnet access:

```text
Status: Disconnected
```

## Meshnet Boot Guard

A systemd oneshot service was added to ensure Meshnet is enabled after boot:

```text
/etc/systemd/system/nordvpn-meshnet.service
```

It is enabled and expected to finish successfully after boot:

```bash
systemctl is-enabled nordvpn-meshnet.service
systemctl is-active nordvpn-meshnet.service
systemctl --no-pager --property=Result,ExecMainStatus show nordvpn-meshnet.service
```

Expected output:

```text
enabled
active
Result=success
ExecMainStatus=0
```

The service re-applies `nordvpn set meshnet on` and verifies that `nordvpn settings` reports:

```text
Meshnet: enabled
```

## Verification Commands

Check the Pi from this Mac:

```bash
ssh pi-mesh 'hostname; uname -r; uptime'
```

Check NordVPN and Meshnet on the Pi:

```bash
nordvpn settings
nordvpn meshnet peer list
systemctl status nordvpnd
systemctl status nordvpn-meshnet.service
```

## ISS Visible Passes

The Pi has an on-demand ISS visible-pass checker:

```bash
ssh pi-mesh iss-next
```

It does not create alerts, background services, cron jobs, or SDR activity. Details are documented in:

```text
iss/ISS.md
```

## Weather

The Pi has an on-demand weather checker for the same configured location:

```bash
ssh pi-mesh weather-now
```

It does not create alerts, background services, cron jobs, or SDR activity. Details are documented in:

```text
weather/WEATHER.md
```
