# Beveiligingsbeleid

[English](SECURITY.md) | **Nederlands**

## Kwetsbaarheid melden

Vond je een beveiligingsprobleem in deze driver, het dashboard of de
helper-scripts, open dan **geen** publiek issue. Mail de maintainer
rechtstreeks:

**almass-only@protonmail.com**

Vermeld:

- Een omschrijving van het probleem en de impact (wat kan een
  aanvaller doen?).
- Reproductiestappen.
- De versie (commit-hash of release-tag).
- Je naam en hoe je gecrediteerd wilt worden in de fix, als je dat
  wilt.

Binnen 7 dagen volgt een eerste reactie. De ernst wordt beoordeeld
tegen de [CVSS 3.1](https://www.first.org/cvss/calculator/3.1)
calculator.

Melders van geldige problemen worden gecrediteerd in
[`CONTRIBUTORS.nl.md`](CONTRIBUTORS.nl.md), tenzij ze anoniem willen
blijven.

## Scope

In scope:

- De kernel-module (`8852au.ko`) — privilege escalation,
  kernel-geheugencorruptie, denial-of-service via geprepareerde
  frames in monitor-mode.
- Het Flask-dashboard (`dashboard/app.py`) — command injection,
  ongeauthenticeerde toegang tot privileged endpoints, path
  traversal.
- De DKMS-scripts (`dkms-install.sh`, `dkms-remove.sh`) — TOCTOU,
  niet-gevalideerde paden, bestanden die root later uitvoert maar die
  een andere gebruiker kan wijzigen.

Buiten scope:

- De inhoud van `tools/`. Dat zijn research/CTF-tools voor
  geautoriseerd testen op systemen die je zelf beheert. Ze zijn
  bewust niet gehard tegen draaien tegen niet-geautoriseerde
  targets — zie `tools/README.md` voor het beleid omtrent
  geautoriseerd gebruik.
- Bugs in de upstream-Realtek-vendor-bron die ongewijzigd in deze
  fork staan. Meld die rechtstreeks bij Realtek.

## Disclosure-tijdlijn

- **Dag 0** — melding ontvangen, binnen 48 uur bevestigd.
- **Dag 7** — eerste assessment + ernst-rating.
- **Dag 30** — fix in een private branch.
- **Dag 60** — gecoördineerde publieke disclosure, CVE aangevraagd
  indien van toepassing.

De maintainer behoudt zich het recht voor om eerder bekend te maken
bij actief misbruikte problemen.

## Gepubliceerde advisories

Alle drie zijn opgelost in `v1.18.1` (2026-11-12). Bijwerken betekent:
pullen, `sudo ./dkms-install.sh` opnieuw draaien, en het dashboard
herstarten als je dat gebruikt.

### Dashboard: SSID-markup plus modprobe.d-injectie geeft root vanuit radiobereik

- **Getroffen:** het dashboard in `v1.15.0.1+8` tot en met `v1.18.0`,
  zolang het draait. De driver zelf speelt geen rol.
- **Impact:** de web-UI toonde SSID's — uit scans, uit monitor-mode-frames,
  van het verbonden netwerk — en de USB-productstring als HTML. Script
  verstopt in een uitgezonden SSID draaide in het dashboard met diens
  inloggegevens, en `/api/advanced` schreef `rtw_country_code`
  ongevalideerd naar `/etc/modprobe.d/8852au.conf`: een newline daarin
  voegde een regel `install 8852au <commando>` toe, die modprobe bij de
  volgende load als root uitvoert (`/api/advanced/reload`). Daarnaast kon
  elke website de browser naar het dashboard laten POSTen (CSRF).
- **Ernst:** CVSS 3.1 8.8 (High),
  `AV:A/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H`; CWE-79, CWE-93.
- **Controle:**
  `grep -vE '^(#|options 8852au |$)' /etc/modprobe.d/8852au.conf` — elke
  regel die dit toont komt niet van het dashboard; beschouw een
  `install`-, `remove`- of `softdep`-regel daar als een compromittering.
- **Oplossing:** update naar `v1.18.1` en herstart het dashboard.

### Driver: private ioctls bereikbaar zonder CAP_NET_ADMIN

- **Getroffen:** elke release; het gat zit in de vendor-code waarmee deze
  fork begon.
- **Impact:** `rtw_ioctl()` controleerde geen enkele capability, en de
  kernel laat het afschermen van `SIOCDEVPRIVATE` aan drivers over — dus
  elke lokale gebruiker kon MAC- en RF-registers schrijven, het kanaalplan
  en het regulatoire land wijzigen, of de driver stoppen via de private en
  Android-commandotabellen.
- **Ernst:** CVSS 3.1 6.6 (Medium),
  `AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H`; CWE-862.
- **Oplossing:** update naar `v1.18.1` en installeer de module opnieuw.

### DKMS-brontree beschrijfbaar voor de installerende gebruiker

- **Getroffen:** installaties via `dkms-install.sh` van `v1.15.0.1+8`
  tot en met `v1.18.0`. Installaties via `make install` niet.
- **Impact:** lokale privilege escalation naar root. De tree onder
  `/usr/src/rtl8852au-<versie>` behield de eigenaar van de checkout,
  terwijl DKMS die tree bij elke kernelupgrade als root herbouwt — dus
  die gebruiker, of alles wat als die gebruiker draait, kon zonder sudo
  code als root laten uitvoeren en, als de DKMS-MOK-sleutel is
  ingeschreven, een ondertekende module laten laden.
- **Ernst:** CVSS 3.1 7.3 (High),
  `AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H`; CWE-732.
- **Controle:**
  `find /usr/src/rtl8852au-* \( ! -user root -o -perm /022 \) -print -quit`
  — geeft dit uitvoer, dan is de installatie getroffen.
- **Oplossing:** update naar `v1.18.1` en draai opnieuw
  `sudo ./dkms-install.sh`. Kan er onbetrouwbare code als eigenaar van
  de checkout hebben gedraaid, verwijder de driver dan met
  `sudo ./dkms-remove.sh` en installeer opnieuw vanuit een verse clone:
  alleen het eigenaarschap aanpassen laat staan wat er intussen is
  geschreven.
- **Details:** [`RELEASE_NOTES_v1.18.1.md`](RELEASE_NOTES_v1.18.1.md).
