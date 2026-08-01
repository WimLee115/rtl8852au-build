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
  niet-gevalideerde paden.

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
