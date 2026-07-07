# rtl8852au-build

[English](README.md) | **Nederlands**

[![CI](https://github.com/WimLee115/rtl8852au-build/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/WimLee115/rtl8852au-build/actions/workflows/ci.yml)
[![Licentie: GPL-2.0](https://img.shields.io/badge/licentie-GPL--2.0-blue.svg)](LICENSE)
[![Kernel](https://img.shields.io/badge/kernel-6.1%20%E2%80%93%207.0%2B-informational.svg)](#compatibiliteit)

Out-of-tree Linux-driver voor USB-WiFi-adapters gebaseerd op de Realtek
**RTL8852AU**- en **RTL8832AU**-chipsets (WiFi 6, AX1800). De upstream
vendor-broncode (`v1.15.0.1-2`) compileert niet meer op moderne kernels;
deze fork draagt een aantal gerichte patches die de build herstellen op
kernel 6.17 en nieuwer en lost daarbij meerdere runtime-bugs op die
zichtbaar werden onder sanitizer-enabled kernels.

De scope van de fork is bewust beperkt: zorg dat de driver blijft
bouwen, hou monitor-mode betrouwbaar en blijf dicht bij de
vendor-broncode zodat upstream-wijzigingen later opnieuw toegepast
kunnen worden.

---

## Inhoudsopgave

- [Wat deze fork wijzigt](#wat-deze-fork-wijzigt)
- [Installatie](#installatie)
- [DKMS-installatie](#dkms-installatie)
- [Ondersteunde apparaten](#ondersteunde-apparaten)
- [Patch-set](#patch-set)
- [Web-dashboard](#web-dashboard)
- [Test suite](#test-suite)
- [Compatibiliteit](#compatibiliteit)
- [Probleemoplossing](#probleemoplossing)
- [Beveiliging](#beveiliging)
- [Bijdragen](#bijdragen)
- [Disclaimer](#disclaimer)
- [Credits](#credits)
- [Licentie](#licentie)

---

## Wat deze fork wijzigt

Ten opzichte van de Realtek vendor-bron `v1.15.0.1-2`:

- **Kernel 6.17+ compatibiliteit** — twaalf compile-time fixes voor
  verwijderde API's en gewijzigde signatures (WEXT-verwijdering,
  `netif_rx`-hernoeming, `proc_ops`, `ndo_get_stats64`, `timer_setup`,
  SKB-header-API, DMA-API, USB-pipe-macros, `access_ok` argumenten,
  implicit fallthrough, `class_create`-signature, cfg80211
  kanaal-switch + MLO `radio_idx`).
- **UBSAN array-out-of-bounds**-fix op elke WPA/WPA2-key-operatie
  (`include/ieee80211.h`).
- **Monitor-mode NULL-deref, SKB use-after-free, race + double-free**
  in `core/rtw_recv.c`.
- **`netdev_close`-race + rmmod-tijdens-associatie panic** —
  `netdev_close()` neemt nu `hw_init_mutex` symmetrisch met
  `netdev_open()` en slaat het disassoc-cmd-pad over zodra het
  apparaat surprise-removed is (`os_dep/linux/os_intfs.c`).
- **Ethtool toont een echte linksnelheid** in plaats van
  `Speed: unknown`.
- **USB-ID's toegevoegd** voor adapters waarvan bevestigd is dat ze de
  RTL8852AU-chipset gebruiken (TP-Link TX20U Plus, TX35U Plus).

Elke wijziging staat in een aparte commit; de post-baseline patches
zijn daarnaast als losstaande `git format-patch`-bestanden
geëxporteerd in [`patches/`](patches/). Zie
[CHANGELOG.md](CHANGELOG.md) voor de volledige historie.

## Installatie

```bash
sudo apt install -y build-essential dkms linux-headers-$(uname -r) git
git clone https://github.com/WimLee115/rtl8852au-build.git
cd rtl8852au-build
make -j"$(nproc)"
sudo make install
sudo modprobe 8852au
```

Verifieer:

```bash
lsmod   | grep 8852au
ip link | grep wlan
dmesg   | grep -iE "8852|rtw"
```

Wordt de adapter wel herkend maar verschijnt er geen `wlan*`-interface,
ontkoppel en steek hem opnieuw in na `modprobe` zodat het
USB-subsysteem opnieuw bindt.

## DKMS-installatie

DKMS herbouwt de module automatisch bij een kernelupgrade.

```bash
sudo apt install -y build-essential dkms linux-headers-$(uname -r) git
git clone https://github.com/WimLee115/rtl8852au-build.git
cd rtl8852au-build
sudo ./dkms-install.sh
```

`dkms-install.sh` leest `PACKAGE_NAME` en `PACKAGE_VERSION` uit
`dkms.conf`, kopieert de broncode naar `/usr/src`, registreert en
bouwt de module via DKMS, en doet ten slotte een `modprobe`.

Verwijderen:

```bash
sudo ./dkms-remove.sh
```

## Ondersteunde apparaten

USB-adapters gebaseerd op de **RTL8852AU**- of
**RTL8832AU**-chipset. De onderstaande tabel wordt gegenereerd uit
`os_dep/linux/usb_intf.c`.

| USB-ID       | Apparaat                       | Chipset    | Status     |
|--------------|--------------------------------|------------|------------|
| `0bda:8832`  | Realtek-referentiebord         | RTL8832AU  | Herkend    |
| `0bda:885a`  | Realtek-referentiebord         | RTL8852AU  | Herkend    |
| `0bda:885c`  | Realtek-referentiebord         | RTL8852AU  | Herkend    |
| `0b05:1997`  | ASUS USB-AX56 (variant)        | RTL8852AU  | Herkend    |
| `0b05:1a62`  | ASUS USB-AX56 (zonder dock)    | RTL8832AU  | Herkend    |
| `0411:0312`  | Buffalo WI-U3-1200AX2(/N)      | RTL8852AU  | Herkend    |
| `2001:0141`  | D-Link DWA-X1850               | RTL8852AU  | Herkend    |
| `2001:3321`  | D-Link DWA-X1850 (variant)     | RTL8852AU  | Herkend    |
| `35bc:0100`  | TP-Link AX1800 (generiek)      | RTL8852AU  | Herkend    |
| `2357:013f`  | TP-Link Archer TX20U Plus      | RTL8852AU  | **Getest** |
| `2357:0140`  | TP-Link AX1800 (variant)       | RTL8852AU  | Herkend    |
| `2357:0141`  | TP-Link AX1800 (variant)       | RTL8852AU  | Herkend    |
| `3625:010f`  | TP-Link Archer TX35U Plus      | RTL8852AU  | Herkend    |
| `056e:4020`  | Elecom WDC-X1201DU3            | RTL8852AU  | Herkend    |

**Getest** betekent dat de maintainer op die specifieke adapter de
binding, associatie en daadwerkelijk verkeer heeft geverifieerd.
**Herkend** betekent dat de USB-ID in de driver staat en de chipset
klopt, maar dat een volledige end-to-end-check nog openstaat.

Een nieuwe ID aanvragen kan via een
[hardware support
request](https://github.com/WimLee115/rtl8852au-build/issues/new?template=hardware_support.yml)
met `lsusb -v`-uitvoer die aantoont dat het apparaat een
RTL8852AU/RTL8832AU-chipset gebruikt.

## Patch-set

De baseline-commit (`2be21aa`) integreert de twaalf
kernel-compatibiliteit-patches die de vendor-broncode nodig heeft om
op Linux 6.17+ te compileren:

| #  | Patch                          | Bestanden                                                | Opmerking                                  |
|----|--------------------------------|----------------------------------------------------------|--------------------------------------------|
| 01 | `cfg80211-wext-removal`        | `os_dep/linux/ioctl_cfg80211.c`                          | cfg80211 verwijderde de WEXT-bridge        |
| 02 | `netif-rx-timestamp`           | `os_dep/linux/recv_linux.c`                              | `netif_rx` → `netif_rx_any_context`        |
| 03 | `proc-ops-compat`              | `os_dep/linux/rtw_proc.c`                                | `proc_ops` in plaats van `file_operations` |
| 04 | `ndo-get-stats-removal`        | `os_dep/linux/os_intfs.c`                                | `ndo_get_stats` → `ndo_get_stats64`        |
| 05 | `timer-setup-macro`            | `core/rtw_mlme_ext.c`, `core/rtw_tdls.c`                 | `timer_setup()`                            |
| 06 | `skb-header-api`               | `core/rtw_recv.c`, `os_dep/linux/recv_linux.c`           | SKB-header-accessor-wijzigingen            |
| 07 | `pci-alloc-consistent`         | `hal/pci/pci_ops.c`                                      | DMA-API vervangt `pci_alloc_consistent`    |
| 08 | `usb-pipe-macros`              | `hal/usb/usb_ops.c`                                      | Strikter USB-pipe type-checking            |
| 09 | `access-ok-args`               | `os_dep/linux/ioctl_linux.c`                             | 2-argument `access_ok()`                   |
| 10 | `implicit-fallthrough`         | meerdere `core/`, `hal/`                                 | `fallthrough;`-annotaties                  |
| 11 | `class-create-api`             | `os_dep/linux/os_intfs.c`                                | `class_create()` verloor het `owner`-arg   |
| 12 | `cfg80211-ch-switch`           | `os_dep/linux/ioctl_cfg80211.c`                          | `cfg80211_ch_switch_notify`-signature      |

Post-baseline fixes (bugfixes, hardware-toevoegingen, build-fixes voor
tussenliggende kernels) staan in [`patches/`](patches/) als
losstaande `git format-patch`-bestanden; ze maken al deel uit van de
huidige boom. Zie [`patches/README.md`](patches/README.md) voor de
index.

## Web-dashboard

Een kleine Flask-app die de runtime-staat van de driver toont samen
met een aantal besturingsknoppen (scannen, verbinden, MTU, txpower,
module-reload). Het dashboard luistert standaard op `127.0.0.1` en
beschermt elk endpoint met HTTP Basic Auth — het wachtwoord is een
host-specifiek token dat bij de eerste run wordt gegenereerd en als
`0600` wordt opgeslagen in `~/.config/rtl8852au/dashboard.token`.

```bash
pip install --require-hashes -r dashboard/requirements.txt
sudo python3 dashboard/app.py
# Open de getoonde URL; gebruikersnaam wordt genegeerd, wachtwoord = het token hierboven.
```

Met `--host 0.0.0.0` stel je het dashboard bloot aan het LAN. Het
auth-token is dan het enige dat tussen het netwerk en root-acties op
deze machine staat — houd het privé.

Een doorloop van elk tabblad, elke knop en een handvol veelvoorkomende
scenario's staat in [`docs/dashboard.nl.md`](docs/dashboard.nl.md).

## Test suite

`tests/test_driver.py` is een Python-`unittest`-suite die de driver
test tegen de draaiende kernel en een aangesloten adapter. Na elke
run wordt een JSON-rapport weggeschreven naar
`tests/test_report.json`.

```bash
sudo ./tests/run_tests.sh                # veilig, niet-destructief
sudo ./tests/run_tests.sh --module       # module + binding (read-only)
sudo ./tests/run_tests.sh --interface    # ifup/ifdown + cfg80211-queries
sudo ./tests/run_tests.sh --scan         # iw-scan trigger + dump
sudo ./tests/run_tests.sh --usb          # USB-endpoint + snelheid
sudo ./tests/run_tests.sh --dmesg        # kernel-log scannen op fouten
```

De destructieve klassen (`TestModuleReload`, `TestStability`) halen
de module weg en wisselen de interface snel op en af. Ze zijn opt-in
en de runner weigert ze te starten zolang `NetworkManager`,
`wpa_supplicant` of een actieve associatie aanwezig is:

```bash
sudo systemctl stop NetworkManager wpa_supplicant
sudo ip link set wlan0 down
sudo ./tests/run_tests.sh --reload       # rmmod + insmod-cyclus
sudo ./tests/run_tests.sh --stability    # rapide ifup/ifdown + scans
sudo ./tests/run_tests.sh --all          # alles, inclusief destructief
```

| Testklasse           | Verifieert                                                            |
|----------------------|-----------------------------------------------------------------------|
| `TestModuleBasics`   | `.ko` bestaat, `modinfo`-vermagic klopt, driver staat in sysfs        |
| `TestDeviceBinding`  | USB-device gebonden, `wlan*` gemaakt, geldig MAC + MTU                |
| `TestInterfaceUp`    | Interface up/down-cyclus is schoon, IFF_UP gezet                      |
| `TestWiFiScan`       | `iw scan trigger` levert een BSS op; 2.4 + 5 GHz banden zichtbaar     |
| `TestCfg80211`       | `iw dev info`, phy-info, managed-mode ondersteund, station dump       |
| `TestProcFS`         | `/proc/net/rtw_*`-entries bestaan (overgeslagen bij CONFIG_PROC_DEBUG=n) |
| `TestUSBEndpoints`   | USB-snelheid ≥ 480 Mbps, minstens twee endpoints aanwezig             |
| `TestDmesgClean`     | Geen `error`/`bug`/`oops`/`panic` in dmesg voor deze driver           |
| `TestModuleReload`   | *(destructief)* `rmmod` + `insmod`; interface komt terug              |
| `TestStability`      | *(destructief)* 10× ifup/ifdown met 1,5 s tussenpauze + 5× scan       |

## Compatibiliteit

| Distributie                  | Kernel             | Architectuur | Geverifieerd door     |
|------------------------------|--------------------|--------------|-----------------------|
| Kali Linux Rolling 2026.1    | 6.19.14+kali-amd64 | x86_64       | Maintainer-hardware   |
| Kali Linux Rolling           | 7.0.12+kali-amd64  | x86_64       | Maintainer-build      |
| Ubuntu 22.04 LTS             | distributie-default | x86_64      | CI-bouw-matrix        |
| Ubuntu 24.04 LTS             | distributie-default | x86_64      | CI-bouw-matrix        |

Andere kernels in het bereik 6.1 LTS → 7.0+ worden verwacht te
compileren omdat elke patch gebonden is aan een
`LINUX_VERSION_CODE`-conditie, maar zijn niet door de maintainer
geverifieerd.

## Probleemoplossing

<details>
<summary><strong>Build faalt met "implicit declaration of function 'wireless_send_event'"</strong></summary>

De patch die de WEXT-verwijzingen verwijdert, is niet aangekomen.
Zorg dat je vanuit deze repository bouwt, niet vanuit een vanilla
[`lwfinger/rtl8852au`](https://github.com/lwfinger/rtl8852au)-checkout,
en doe een schone build:

```bash
make clean
make -j"$(nproc)"
```
</details>

<details>
<summary><strong><code>modprobe 8852au</code> meldt "module not found"</strong></summary>

```bash
sudo depmod -a
sudo modprobe 8852au
find /lib/modules/"$(uname -r)" -name '8852au.ko*'
```
</details>

<details>
<summary><strong>Adapter aangesloten maar geen <code>wlanX</code> verschijnt</strong></summary>

```bash
lsusb | grep -iE "realtek|tp-link|d-link|asus"
dmesg | tail -30
sudo modprobe -r 8852au && sudo modprobe 8852au
```

Als het apparaat wel in `lsusb` staat maar er geen interface verschijnt,
ontbreekt de USB-ID waarschijnlijk in de driver-tabel. Open een
hardware-support-request met `lsusb -v -d VVVV:PPPP`-uitvoer.
</details>

<details>
<summary><strong>Monitor-mode: <code>iw dev wlanX set type monitor</code> faalt</strong></summary>

```bash
sudo ip link set wlan1 down
sudo iw dev wlan1 set type monitor
sudo ip link set wlan1 up
```

Als `NetworkManager` ertussen gaat zitten, stop het of markeer de
interface unmanaged in `/etc/NetworkManager/NetworkManager.conf`:

```ini
[keyfile]
unmanaged-devices=interface-name:wlan1
```
</details>

<details>
<summary><strong>USB 3.0-adapter haalt slechts ~100 Mbps</strong></summary>

```bash
lsusb -t | grep 8852         # moet "5000M" tonen; "480M" = teruggevallen naar USB 2.0
```

Klopt de linksnelheid wel maar is de throughput laag, schakel
agressieve power-management uit:

```bash
echo 'options 8852au rtw_power_mgnt=0' | sudo tee /etc/modprobe.d/8852au.conf
sudo modprobe -r 8852au && sudo modprobe 8852au
```
</details>

<details>
<summary><strong>Secure Boot: "module verification failed: signature and/or required key missing"</strong></summary>

Onderteken de pas-gebouwde module met je Machine Owner Key (MOK):

```bash
sudo /usr/src/linux-headers-"$(uname -r)"/scripts/sign-file \
    sha256 \
    /var/lib/shim-signed/mok/MOK.priv \
    /var/lib/shim-signed/mok/MOK.der \
    /lib/modules/"$(uname -r)"/updates/dkms/8852au.ko
```

Heb je nog geen MOK, enroll er een met `mokutil --import`, herstart en
volg de prompt, en onderteken daarna opnieuw.
</details>

## Beveiliging

- Kwetsbaarheidsmeldingen gaan naar de maintainer op het adres in
  [`SECURITY.md`](SECURITY.md), niet via publieke issues.
- De repository heeft [private vulnerability
  reporting](https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/configuring-private-vulnerability-reporting-for-a-repository)
  aanstaan.
- Firmware-blobs worden bijgehouden in
  [`CHECKSUMS.sha256`](CHECKSUMS.sha256) en bij elke CI-build
  geverifieerd.
- Het dashboard luistert standaard op loopback en vereist HTTP Basic
  Auth op elk endpoint.

## Bijdragen

Zie [`CONTRIBUTING.md`](CONTRIBUTING.md) voor scope,
bug-report-richtlijnen, hardware-toevoegingen en de
vendor-stijl-vereiste voor driver-source-patches. Kort samengevat:

- Eén logische wijziging per commit; vendor-stijl voor `core/`,
  `hal/`, `os_dep/` (tabs, K&R-braces, geen grote herformatteringen).
- Python (`dashboard/`, `tests/`, `tools/`) moet door `ruff check`
  komen met de config in [`ruff.toml`](ruff.toml).
- Shell moet door `shellcheck` komen.
- CI moet groen zijn vóór merge; branch-protection op `main` dwingt
  dit af.

## Disclaimer

Dit is een **onafhankelijke community-fork**. Geen affiliatie met,
endorsement door of sponsoring vanuit **Realtek Semiconductor
Corp.**, **TP-Link Technologies**, **ASUSTeK Computer Inc.**,
**D-Link Corporation**, **Buffalo Inc.**, **Elecom Co., Ltd.** of
welke andere hardware-vendor dan ook genoemd in deze repository.
Productnamen en USB-ID's worden uitsluitend ter identificatie genoemd.

De firmware-blob in
[`phl/hal_g6/mac/fw_ax/rtl8852a/hal8852a_fw.c.xz`](phl/hal_g6/mac/fw_ax/rtl8852a/hal8852a_fw.c.xz)
is © Realtek Semiconductor Corp. en wordt **ongewijzigd**
gedistribueerd uit de Realtek-`v1.15.0.1-2`-vendor-bundel. De
SHA-256 staat in [`CHECKSUMS.sha256`](CHECKSUMS.sha256) en wordt door
CI bij elke build geverifieerd.

Zoals bij elke out-of-tree-kernelmodule wordt de software
**geleverd "AS IS" zonder enige garantie**, conform de
[GPL-2.0-licentie](LICENSE) waaronder deze wordt verspreid.

## Credits

- **Realtek Semiconductor Corp.** — originele vendor-driver
  (`v1.15.0.1-2`).
- **[lwfinger](https://github.com/lwfinger)** — langjarige
  community-Linux-packaging.
- **[morrownr](https://github.com/morrownr)** — USB-WiFi-adapter
  documentatie, USB-ID-referenties, onderhoudspatronen.
- **[Joan Sala (`jsiwrk`)](https://github.com/jsiwrk)** — TP-Link
  Archer TX35U Plus USB-ID (PR #3).
- **[WimLee115](https://github.com/WimLee115)** — fork-onderhoud,
  kernel-compatibiliteit-patches, test suite, dashboard.

## Licentie

GNU General Public License v2.0 — zie [`LICENSE`](LICENSE). De
driver komt uit Realtek's GPL-broncode; elke wijziging in deze
repository valt onder dezelfde licentie.

```
SPDX-License-Identifier: GPL-2.0
```
