# Raspberry Pi Setup

Initial setup date: 2026-06-05

Tailscale and Termius access verified: 2026-10-02

## Device

- Hostname: `pi`
- User: `pi`
- OS: Ubuntu 24.04.4 LTS
- Architecture: `aarch64`
- Kernel shown in the Termius login banner on 2026-10-02: `6.8.0-1060-raspi`

## Connected Hardware

- Nooelec RTL-SDR v5 SDR, NESDR SMArt HF/VHF/UHF, RTL2832U and R820T2/R860 based.
- Bingfu dual-band 978 MHz / 1090 MHz 7 dBi magnetic base antenna.

Ubuntu detects the SDR as:

```text
Bus 004 Device 002: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T
```

## Network

Use Tailscale for remote access. The client device must be connected to the tailnet and able to reach the Pi.

```text
Hostname: pi
Tailscale IPv4: 100.75.237.100
SSH user: pi
SSH port: 22
```

Primary SSH command from this Mac:

```bash
ssh pi
```

The original home LAN address remains configured as a fallback when on the same network:

```bash
ssh pi-ubuntu
```

That alias uses `192.168.1.193`. LAN access was not retested on 2026-10-02.

## SSH Setup

Passwordless SSH uses the existing local private key:

```text
/Users/francesco/.ssh/codex/pi-ubuntu
```

Its public key was installed in `/home/pi/.ssh/authorized_keys` during the original setup. Keep the private key outside this repository.

The effective settings in `/Users/francesco/.ssh/config` were checked on 2026-10-02:

```sshconfig
Host pi
  HostName 100.75.237.100
  User pi
  Port 22
  IdentityFile /Users/francesco/.ssh/codex/pi-ubuntu
  IdentitiesOnly yes

Host pi-ubuntu
  HostName 192.168.1.193
  User pi
  IdentityFile /Users/francesco/.ssh/codex/pi-ubuntu
  IdentitiesOnly yes
```

This uses SSH key authentication over the Tailscale network. The connection check did not establish whether Tailscale SSH is enabled on the Pi.

## Termius

The saved connection in Termius is:

| Setting | Value |
| --- | --- |
| Host label | Pi |
| Address | 100.75.237.100 |
| Protocol / port | SSH / 22 |
| Username | pi |
| Vault | Personal |
| SSH key label | Pi — Tailscale |
| Key type | ED25519 |

The existing `/Users/francesco/.ssh/codex/pi-ubuntu` key was imported into the Personal vault with the owner's approval. Termius may sync the saved key through the account.

To connect, enable Tailscale on the client, open Termius, and connect to **Pi**. To recreate the configuration, add a host with the settings above, import the existing key through **Keychain → New key → Import from key file**, then select **Pi — Tailscale** under the host's SSH credentials.

Verification on 2026-10-02:

- A batch-mode SSH connection from this Mac succeeded; `hostname` and `whoami` both returned `pi`, and `tailscale ip -4` returned `100.75.237.100`.
- Termius opened an authenticated Ubuntu session with the `pi@pi:~$` prompt.
- The Termius login banner reported that a system restart was required. No update or reboot was performed as part of this connection setup.

## System Updates

During the original June setup, the Pi was updated:

```bash
sudo apt update
sudo apt -y upgrade
sudo reboot
```

After that reboot, the Pi came back online and no further reboot was required at the time. See the dated Termius verification above for the later restart notice.

## Historical NordVPN And Meshnet Setup

The following records the June 2026 setup. Tailscale is now the verified access path; the current state of NordVPN and its boot guard was not checked on 2026-10-02. The old `pi-mesh` alias used `100.100.117.13` (`francesco.dicostanzo-andes.nord`).

NordVPN was installed using the official Linux CLI installer:

```bash
sh <(curl -sSf https://downloads.nordcdn.com/apps/linux/install.sh)
```

Installed version:

```text
NordVPN Version 5.0.0
```

The installer added user `pi` to the `nordvpn` group.

The NordVPN daemon was enabled and active at setup:

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

NordVPN settings recorded at setup:

```text
Technology: NORDLYNX
Firewall: enabled
User Consent: disabled
Auto-connect: disabled
Meshnet: enabled
```

The VPN tunnel was disconnected at setup, while Meshnet was enabled:

```text
Status: Disconnected
```

### Historical Meshnet Boot Guard

A systemd oneshot service was added to ensure Meshnet is enabled after boot:

```text
/etc/systemd/system/nordvpn-meshnet.service
```

It was enabled and verified to finish successfully after boot:

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
ssh pi 'hostname; uname -r; uptime'
```

Check the Tailscale address and peer status on the Pi:

```bash
ssh pi 'tailscale ip -4; tailscale status'
```

## ISS Visible Passes

The Pi has an on-demand ISS visible-pass checker:

```bash
ssh pi iss-next
```

It does not create alerts, background services, cron jobs, or SDR activity. Details are documented in:

```text
iss/ISS.md
```

## Weather

The Pi has an on-demand weather checker for the same configured location:

```bash
ssh pi weather-now
```

It does not create alerts, background services, cron jobs, or SDR activity. Details are documented in:

```text
weather/WEATHER.md
```
