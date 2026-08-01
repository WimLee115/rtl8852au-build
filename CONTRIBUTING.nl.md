# Bijdragen

[English](CONTRIBUTING.md) | **Nederlands**

Deze fork wordt in zijn vrije tijd onderhouden door één developer.
Bijdragen zijn welkom — houd ze gefocust en goed beschreven.

## Wat past binnen de scope

- Compatibiliteitspatches voor nieuwere Linux-kernels (6.20, 6.21, …).
- Bugfixes voor monitor-mode, USB-suspend en het RX/TX-pad.
- USB-ID-toevoegingen voor adapters waarvan bevestigd is dat ze de
  RTL8852AU/RTL8832AU-chipset gebruiken.
- Dashboard-verbeteringen, extra API-endpoints.
- Meer tests in `tests/test_driver.py`.

## Wat niet binnen de scope past

- Ondersteuning voor andere Realtek-chipsets (RTL8852B/RTL8852C). Daar
  zijn aparte forks voor; deze blijft gefocust op RTL8852AU/8832AU.
- Het volledig herformatteren van de vendor-broncode. De driver-code
  volgt bewust Realtek's originele stijl — dat maakt upstream-syncing
  mogelijk.
- Forks van het dashboard voor niet-gerelateerde use-cases.

## Bug reports

Gebruik het **bug report**-issue-template:

- USB-ID (`lsusb | grep -i realtek`) en kernel-versie (`uname -r`).
- `dmesg | grep -iE "8852|rtl"`-output.
- Build-log als de build faalt.
- Of het reproduceerbaar is in managed-mode, monitor-mode of beide.

Voor nieuwe hardware gebruik het **hardware support
request**-template.

## Hardware-toevoegingen

Bewerk `os_dep/linux/usb_intf.c` om een USB-ID toe te voegen en plaats
de entry binnen `rtw_usb_id_tbl[]` onder de juiste vendor-sectie. De
opbouw is:

```c
{USB_DEVICE_AND_INTERFACE_INFO(0xVVVV, 0xPPPP, 0xff, 0xff, 0xff), .driver_info = RTL8852A},
```

Voeg in de PR-beschrijving toe:

- `lsusb -v -d VVVV:PPPP`-output (fabrikant- + product-strings).
- Bewijs dat het apparaat de RTL8852AU- of RTL8832AU-chipset gebruikt
  (FCC ID-lookup, vendor-datasheet, dmesg na binding).
- Bevestiging dat je de wijziging tegen het apparaat hebt getest — op
  zijn minst dat de driver laadt en een interface wordt aangemaakt.

## Code-wijzigingen indienen

1. Fork en maak een topic-branch.
2. Houd elke commit beperkt tot één logische wijziging. Voor
   driver-patches: gebruik het formaat van de Linux-kernel-community
   — korte subject-regel gevolgd door een paragraaf die uitlegt
   *waarom* de wijziging nodig is.
3. Draai de test suite (`sudo ./tests/run_tests.sh`) en bevestig dat
   `make` op minstens één recente kernel slaagt (6.12 LTS of nieuwer).
4. Open een PR. CI bouwt op Ubuntu 22.04 + 24.04 en draait lint.

Zodra je PR gemerged is, verschijn je automatisch in de
GitHub-contributors-grafiek; substantiële bijdragen worden bovendien
vermeld in [`CONTRIBUTORS.nl.md`](CONTRIBUTORS.nl.md).

### Stijl

- Driver-source: volg Realtek's vendor-stijl (tabs, K&R-braces, geen
  Lindent-herformattering).
- Python (`dashboard/`, `tests/`, `tools/`): conservatief — moet door
  `ruff check` komen met de config in `ruff.toml`.
- Shell: moet door `shellcheck` komen.

## Release-proces

De maintainer tagt releases volgens SemVer `vMAJOR.MINOR.PATCH`
(bijvoorbeeld `v1.16.0`). CI bouwt artefacten; zodra die groen
zijn wordt een GitHub-release uitgebracht met de CHANGELOG-entry
gekopieerd uit `CHANGELOG.md`.
