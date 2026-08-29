# Bijdragers

[English](CONTRIBUTORS.md) | **Nederlands**

Iedereen die heeft geholpen **rtl8852au-build** te maken tot wat het is.
Dit weerspiegelt de credits in de [README](README.nl.md) en de
[CHANGELOG](CHANGELOG.md); de GitHub-[contributors-grafiek](https://github.com/WimLee115/rtl8852au-build/graphs/contributors)
wordt automatisch gegenereerd uit de commit-historie.

## Maintainer

- **[WimLee115](https://github.com/WimLee115)** — fork-onderhoud, de twaalf
  kernel 6.17+ compatibiliteitspatches, de kernel 7.1 cfg80211/pppoe-port,
  de monitor-mode-crashfixes, DKMS-packaging, het Flask-dashboard, de test
  suite en CI.

## Bijdragers

- **[Joan Sala — `jsiwrk`](https://github.com/jsiwrk)** — TP-Link Archer
  TX35U Plus USB-ID (`3625:010f`) en de kernel 6.8-buildfix
  ([PR #3](https://github.com/WimLee115/rtl8852au-build/pull/3)).
- **[74Thirsty — `gadgetsaavy`](https://github.com/74Thirsty)** — D-Link
  DWA-1850 USB-ID (`2001:332c`) en testen op Parrot OS 6/7
  ([PR #14](https://github.com/WimLee115/rtl8852au-build/pull/14)).
- **[Omelug](https://github.com/Omelug)** — hardwarerapport voor `0bda:8832`
  op kernel 7.0.12, waarmee twee bugs in de test suite aan het licht kwamen:
  het modulepad was hardgecodeerd op een in-tree build, en adapters achter
  een USB-hub golden als niet-gebonden
  ([issue #43](https://github.com/WimLee115/rtl8852au-build/issues/43)).
  Draaide de suite na de fix opnieuw en bevestigde associatie en monitor
  mode, waarmee die ID op *Getest (melder)* kwam.
- **[PierreGrillet](https://github.com/PierreGrillet)** — crashrapporten op
  een TP-Link Archer TX35U Plus die twee driverbugs aan het licht brachten:
  een NULL-deref in de connect-statemachine op een verouderd bericht na een
  mislukte WPA-poging, en een free in atomic context in de
  beacon-pool-opruiming bij hardhandige USB-verwijdering tijdens AP-modus
  ([issue #52](https://github.com/WimLee115/rtl8852au-build/issues/52)).

## Acknowledgements

Geen commit-bijdragers aan deze repo, maar deze fork bouwt voort op hun
werk:

- **Realtek Semiconductor Corp.** — de originele vendor-driver
  (`v1.15.0.1-2`) waarop deze fork is gebaseerd.
- **[lwfinger (Larry Finger)](https://github.com/lwfinger)** — langjarige
  community-Linux-packaging van de Realtek-WiFi-drivers.
- **[morrownr](https://github.com/morrownr)** — USB-WiFi-adapter-documentatie,
  USB-ID-referenties en onderhoudspatronen.

## Jezelf toevoegen

Nieuwe bijdragen zijn welkom — zie [CONTRIBUTING.nl.md](CONTRIBUTING.nl.md).
Open een pull request; zodra die gemerged is, verschijn je automatisch in
de GitHub-contributors-grafiek, en substantiële wijzigingen worden hier en
in de README-credits vastgelegd.

---

*Bots (bijv. Dependabot) die in de commit-historie voorkomen, worden bewust
uit deze lijst weggelaten.*
