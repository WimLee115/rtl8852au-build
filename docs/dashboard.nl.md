# Dashboard-handleiding

[English](dashboard.md) | **Nederlands**

Het dashboard is een kleine Flask-app die de runtime-staat van de
`8852au`-driver toont samen met een aantal operationele
besturingsopties — scannen, verbinden, interface-parameters wijzigen,
de test-suite draaien, driver-module-parameters bewerken. Het draait
lokaal op de host, luistert standaard op loopback en is beschermd met
HTTP Basic Auth.

Deze handleiding loopt door elk tabblad en elke knop, met daarnaast
een aantal veelvoorkomende scenario's.

---

## Inhoudsopgave

- [Eerste keer opzetten](#eerste-keer-opzetten)
- [Inloggen](#inloggen)
- [Tabbladen](#tabbladen)
  - [Overzicht](#overzicht)
  - [Netwerken](#netwerken)
  - [Monitor](#monitor)
  - [Instellingen](#instellingen)
  - [Tests](#tests)
  - [Geavanceerd](#geavanceerd)
- [Taal-switcher](#taal-switcher)
- [Veelvoorkomende scenario's](#veelvoorkomende-scenarios)
- [Probleemoplossing](#probleemoplossing)

---

## Eerste keer opzetten

1. Installeer afhankelijkheden (eenmalig, hash-locked) in een virtuele
   omgeving. De systeem-Python van Debian/Kali is externally-managed
   (PEP 668) en weigert een kale `pip install`:
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install --require-hashes -r dashboard/requirements.txt
   ```
2. Start het dashboard met diezelfde interpreter. Het heeft root nodig
   om `iw`, `wpa_supplicant`, `modprobe` en `dhclient` aan te roepen:
   ```bash
   sudo ./.venv/bin/python3 dashboard/app.py
   ```
3. De eerste start genereert een auth-token in
   `~/.config/rtl8852au/dashboard.token` (mode `0600`). Het token
   blijft tussen herstarts geldig, dus je browser onthoudt het
   wachtwoord.
4. Open de getoonde URL — standaard `http://127.0.0.1:8080/`.

## Inloggen

Elke pagina en elk `/api/*`-endpoint is beschermd met HTTP Basic
Auth:

- **Gebruikersnaam:** maakt niet uit (wordt genegeerd)
- **Wachtwoord:** het token uit de startup-log of uit
  `~/.config/rtl8852au/dashboard.token`

De browser cachet de credentials per sessie, dus je ziet de prompt
alleen de eerste keer na een herstart.

Het dashboard blootstellen aan het LAN (`--host 0.0.0.0`) kan, maar is
opt-in: het token is dan het enige dat tussen het netwerk en
root-operaties op de host staat — behandel het als een wachtwoord.

---

## Tabbladen

### Overzicht

Het standaardvenster bij openen. Vier kaarten die de live staat van
de adapter samenvatten:

| Kaart              | Wat het toont                                                                                       |
|--------------------|-----------------------------------------------------------------------------------------------------|
| **Adapter Info**   | Interface-naam, MAC-adres, IP-adres, UP/DOWN-status, MTU, USB-snelheid en het USB VID:PID            |
| **Verbinding**     | Bij associatie: SSID, signaalsterkte (dBm + kleurbalk), frequentie, huidige TX-bitrate              |
| **Statistieken**   | TX/RX bytes, TX/RX pakketten, fouten en gedropt — acht tegels, elke ~2 s ververst via SSE           |
| **Driver Info**    | Modulenaam, drivernaam, kernel-versie, `srcversion`-hash, vendor-versie                              |
| **Trends**         | Vier sparklines over de laatste 60 minuten: signaal (dBm), TX-bitrate (Mbps), RX-doorvoer (B/s), fout-rate (Δ per sample). De huidige waarde staat rechts naast elke lijn |

Een status-badge rechtsboven toont in één oogopslag **Verbonden**
(groen) of **Niet verbonden** (rood), plus de driver-laad-status.

Het dashboard pusht status-updates via een lange `/api/stream`
Server-Sent-Events-verbinding. Er is geen poll-interval om af te
stellen — nieuwe data komt binnen ~2 s na elke wijziging binnen.

### Netwerken

Drie kaarten. De eerste visualiseert het spectrum, de tweede is de
klassieke AP-tabel, de derde is handmatig verbinden.

**Kanaal-bezetting** (bovenste kaart)

Twee canvassen — één voor 2,4 GHz (kanalen 1–14), één voor 5 GHz
(kanalen 36–165). Elke balk is één kanaal:

| Visueel signaal     | Betekenis                                                              |
|---------------------|------------------------------------------------------------------------|
| Balk-**hoogte**     | Sterkste RSSI op dat kanaal (-90 tot -20 dBm)                          |
| Balk-**kleur**      | Groen bij 1 AP, oranje bij 2, rood bij 3+ (vermoedelijk druk)          |
| Getal boven balk    | Aantal APs op dat kanaal                                               |
| Y-as-labels         | -30 / -50 / -70 / -90 dBm grid-lijnen                                  |

De kaart ververst zichzelf elke 30 s zolang de Netwerken-tab actief
is, en de scan wordt 30 s server-side gecached zodat heen-en-weer
schakelen tussen tabs geen nieuwe `iw scan`-cyclus triggert. Een
één-regel-samenvatting onder de titel toont `N APs verdeeld over M
kanalen`.

**Beschikbare netwerken**

| Knop / kolom       | Betekenis                                                              |
|--------------------|------------------------------------------------------------------------|
| **Scannen**        | Triggert `iw dev <iface> scan`; de tabel vult zich met resultaten      |
| **SSID**           | Netwerknaam; "(Verborgen)" als het AP de naam niet broadcast           |
| **BSSID**          | Het MAC-adres van het AP                                               |
| **Signaal**        | RSSI in dBm met een groen/geel/oranje/rode balk                         |
| **Freq**           | Centrumfrequentie in MHz                                                |
| **Beveiliging**    | Gedetecteerde encryptie (WPA2, WPA3, …, of `--` voor open)             |
| **Verbind**        | Eén klik vult de SSID alvast in het manuele verbindingsformulier        |

**Handmatig verbinden**

- **SSID** — 1–32 bytes, UTF-8 toegestaan.
- **Wachtwoord** — leeg laten voor een open netwerk. Anders 8–63
  tekens volgens de WPA-spec.
- **Verbinden** — schrijft een tijdelijke `wpa_supplicant.conf`,
  stopt eventuele bestaande supplicant voor deze interface, start een
  nieuwe en draait `dhclient`. SSID en passphrase worden geëscaped
  voordat ze in het conf-bestand belanden, dus een `"` in de naam
  breekt de parser niet.
- **Verbreken** — stopt `wpa_supplicant`, geeft de DHCP-lease vrij en
  haalt de interface omlaag.

### Monitor

De vlaggenschip-feature van de driver in één tab. Drie kaarten:

**Modus + interface-status**

De bovenste kaart toont de huidige interface, modus (`managed` /
`monitor` / `unspec`) en kanaal, plus twee knoppen:

- **Monitor inschakelen** — draait `ip link down` → `iw dev … set
  type monitor` → `ip link up`. Als een kanaal is gekozen in de
  picker eronder, wordt dat in dezelfde stap gezet.
- **Terug naar managed** — symmetrisch omgekeerd. Eventuele
  lopende capture wordt eerst gestopt.

Een gele waarschuwing boven de knoppen herinnert je eraan dat
NetworkManager en `wpa_supplicant` de interface eerst moeten
loslaten. Het dashboard kan dat niet voor je doen; draai

```bash
sudo nmcli device set wlan1 managed no
sudo systemctl stop wpa_supplicant
```

eenmalig, en wissel daarna.

**Kanaal-keuze**

Een `<select>` gegroepeerd op 2,4 GHz (kanalen 1–14) en 5 GHz
(36–165). Het huidige kanaal staat voorgeselecteerd. **Toepassen**
draait `iw dev … set channel N`. Als je regulatoire-domein of de
driver het kanaal afwijst, verschijnt de fout als een toast — de
picker filtert niet pro-actief.

**Frame-capture**

Spawnt twee `tcpdump`-processen parallel: één schrijft een `pcap`
naar `/tmp/rtw_monitor.pcap` voor de **.pcap downloaden**-knop
(open in Wireshark), de andere produceert tekstregels die de live
frame-tabel voeden.

| Knop                  | Wat het doet                                                  |
|-----------------------|---------------------------------------------------------------|
| **Capture starten**   | Spawnt beide tcpdumps. Uitgeschakeld zolang je niet in monitor-modus zit. |
| **Capture stoppen**   | Beëindigt beide. Het pcap-bestand blijft staan voor export.   |
| **.pcap downloaden**  | Slaat het bestand op met `Content-Type: application/vnd.tcpdump.pcap` zodat Wireshark het direct opent. |
| **Filter** (input)    | Case-insensitive substring-match tegen type / SSID / src / dst / raw. |
| Frame-tabel           | Nieuwste eerst, gelimiteerd op 200 rijen. Tijd, type, bron-MAC, bestemmings-MAC, SSID (voor management-frames), RSSI. |

De tabel ververst elke 2 seconden zolang de Monitor-tab actief is
en de capture loopt. Wisselen van tab pauzeert het verversen; de
capture zelf blijft draaien totdat je op Stoppen klikt.

### Instellingen

Live interface-tweaks die direct effect hebben (geen module-herstart
nodig).

| Knop                | Wat het doet                                                                  | Bereik         |
|---------------------|-------------------------------------------------------------------------------|----------------|
| **MTU**             | Maximum transmission unit — `ip link set <iface> mtu N`                       | 576 – 9000     |
| **TX Power (dBm)**  | Zendvermogen — `iw dev <iface> set txpower fixed N*100`                       | 0 – 30         |
| **Power Save**      | Toggle `iw dev <iface> set power_save on|off`                                  | aan / uit      |
| **Toepassen**       | Stuurt de formulierwaarden naar `/api/ifconfig`. Waarden buiten het bereik worden stilzwijgend overgeslagen |

### Tests

Draait de Python-`unittest`-suite uit `tests/test_driver.py` en
toont de uitvoer inline.

- **Tests Draaien** — roept `/api/tests/run` aan. De knop toont een
  spinner zolang de suite draait.
- **Output-paneel** — volledige stdout, met `... ok`, `FAIL` en
  `ERROR` in kleur.
- **Samenvatting-regel** — geslaagd / totaal, plus aantallen gefaald
  / fouten / overgeslagen uit `tests/test_report.json`.

Vanuit het dashboard draaien alleen de veilige (niet-destructieve)
testklassen. Wil je `TestModuleReload` en `TestStability` uitvoeren,
draai dan `./tests/run_tests.sh --all` vanuit een terminal — de
runner vereist dat NetworkManager / wpa_supplicant gestopt zijn.

### Geavanceerd

Een Windows-Apparaatbeheer-achtige editor voor **driver
module-parameters**. Dit zijn opties die de driver bij het laden
registreert bij de kernel; ze aanpassen vereist een module-herstart.

Indeling:

- **Linkerkolom** — categorieën (Draadloze Modus, Kanaal &
  Bandbreedte, Energiebeheer, Prestaties, Antenne & Beamforming,
  Roaming & Verbinding, Debug & Geavanceerd).
- **Middenkolom** — eigenschappen in de geselecteerde categorie. Een
  geel stipje naast een naam betekent dat er een onopgeslagen
  wijziging is.
- **Rechterkolom** — editor voor de geselecteerde eigenschap:
  - **Eigenschapsnaam** + een badge `Module parameter — herstart
    nodig`.
  - Een `<select>` voor enumeraties (Uit / Aan / Auto / …) of een
    `<input type="text">` voor numerieke/bitmask-waarden.
  - **Huidige waarde (actief)** — wat de driver nu echt gebruikt.
  - **Opgeslagen (wacht op herstart)** — waarde die naar
    `/etc/modprobe.d/8852au.conf` is geschreven maar nog niet door
    de kernel geladen.
  - **Omschrijving** — een paar zinnen over wat de parameter doet,
    wat de veilige standaardwaarden zijn en wat de afweging is.

Acties onderaan:

- **Opslaan & Toepassen** — schrijft pending wijzigingen naar
  `/etc/modprobe.d/8852au.conf`. Laadt ze nog niet.
- **Standaard Herstellen** — vergeet lokale pending wijzigingen
  (alleen in-memory; reeds-opgeslagen waarden blijven).
- **Module Herladen** — `rmmod 8852au` + `modprobe 8852au` zodat de
  opgeslagen opties actief worden. **De WiFi-verbinding valt
  kortstondig weg** terwijl de module herstart.

De gele banner onder de tab verschijnt zodra je onopgeslagen of
opgeslagen-maar-nog-niet-toegepaste wijzigingen hebt, met op één
regel wat je vervolgens moet klikken.

---

## Taal-switcher

De twee knoppen rechtsboven (**EN** / **NL**) wisselen de hele UI
tussen Engels en Nederlands. De keuze wordt bewaard in
`localStorage`, dus na een refresh blijft je voorkeur. Bij een
verse browser kiest het dashboard automatisch: een Nederlandse
browser opent in het Nederlands, alle andere in het Engels.

## Thema

Twee andere knoppen in de header — **●** (donker) en **○** (licht)
— wisselen de hele UI tussen een donker- en een licht-thema. Net
als de taalkeuze wordt het bewaard in `localStorage`. De sparklines
en spectrum-canvassen pakken de accentkleur van het thema
automatisch op.

## Sneltoetsen

| Toets      | Actie                                              |
|------------|----------------------------------------------------|
| `1`–`5`    | Spring naar de bijbehorende tab                    |
| `/`        | Open Netwerken en start een scan                   |
| `r`        | Ververs status / driver-info / trends              |
| `t`        | Wissel thema (donker ↔ licht)                      |
| `l`        | Wissel taal (EN ↔ NL)                              |
| `?`        | Open de sneltoetsen-help                           |
| `Esc`      | Sluit de overlay                                   |

Sneltoetsen worden onderdrukt zolang een input, select of textarea
focus heeft, zodat ze nooit botsen met het typen van een SSID of
wachtwoord.

---

## Veelvoorkomende scenario's

### Verbinden met een AP die ik nog niet heb gezien

1. **Netwerken** → **Scannen**. Wacht een paar seconden.
2. Klik op **Verbind** naast de SSID in de tabel — die vult het
   manuele verbindingsformulier in.
3. Typ het wachtwoord, klik **Verbinden** in het formulier.
4. De status-badge in de header wordt groen en het **Overzicht**-tab
   toont het live signaal en de bitrate.

### Testen of de adapter normale snelheid haalt

1. **Overzicht** — bekijk de huidige **TX bitrate** onder
   *Verbinding*. WiFi 6 op 80 MHz haalt ~1200 Mbps bij sterk
   signaal; alles boven 500 Mbps is gezond voor een desktop-scenario.
2. Check **USB Snelheid** onder *Adapter Info*. `5000 Mbps` is USB 3
   (goed). `480 Mbps` betekent dat de adapter is teruggevallen naar
   USB 2, wat de doorvoer beperkt tot ~300 Mbps. Probeer een andere
   USB-poort, bij voorkeur direct op het moederbord.
3. **Statistieken** — let op *TX/RX fouten* en *dropped*. Beide
   moeten dichtbij nul blijven. Een oplopende fouten-teller wijst
   meestal op een zwak signaal of een rumoerige omgeving.

### De adapter rustiger maken op een laptop

1. Tab **Instellingen**.
2. Zet **Power Save** op **Aan** en **TX Power** op iets bescheidens
   (bijv. 15 dBm). Klik **Toepassen**.
3. Voor een diepgaandere wijziging: open **Geavanceerd** →
   *Energiebeheer* en zet `rtw_power_mgnt` op **Maximaal**. Klik
   **Opslaan & Toepassen**, daarna **Module Herladen**.

### Een nieuwe driver-instelling proberen en kunnen terugrollen

1. **Geavanceerd** — wijzig de eigenschap; het gele stipje
   verschijnt.
2. **Opslaan & Toepassen** schrijft 'm naar
   `/etc/modprobe.d/8852au.conf`.
3. **Module Herladen** — als de adapter zich beter gedraagt, ben je
   klaar.
4. Werkt iets niet meer, open **Geavanceerd** opnieuw, zet de
   eigenschap terug, **Opslaan & Toepassen** + **Module Herladen**.
   In het ergste geval: verwijder `/etc/modprobe.d/8852au.conf` en
   `sudo modprobe -r 8852au && sudo modprobe 8852au`.

---

## Probleemoplossing

**Het dashboard start niet: `Address already in use`**

Een ander exemplaar draait nog. Stop dat eerst:

```bash
sudo fuser -k 8080/tcp
```

Of draai het nieuwe exemplaar op een andere poort:

```bash
sudo ./.venv/bin/python3 dashboard/app.py --port 9090
```

**De browser blijft elke refresh om login vragen**

De browser cachet de Basic Auth credentials niet (sommige
privacy-extensies halen ze weg). Installeer een eigen
cookie/credentials-extensie die `127.0.0.1` whitelist, of open de URL
met het token erin verwerkt:

```
http://anything:TOKEN@127.0.0.1:8080/
```

(Firefox en Chromium accepteren dit op loopback; voor andere hosts
weigeren ze `user:pass@…`.)

**Het Overzicht-tab toont "No interface found"**

Het dashboard vond geen `wlan*`-device gebonden aan `rtl8852au`.
Verifieer dat de module geladen is en het apparaat herkend wordt:

```bash
lsmod | grep 8852au
ip link | grep wlan
dmesg | tail -20
```

Is het apparaat aangesloten maar verschijnt er geen `wlan*`, draai
`sudo modprobe -r 8852au && sudo modprobe 8852au`, of controleer of
de USB-ID in [`os_dep/linux/usb_intf.c`](../os_dep/linux/usb_intf.c)
staat.

**Een eigenschap in Geavanceerd is "Niet beschikbaar"**

Die module-parameter is niet gecompileerd in de huidige
`8852au.ko`. Doorgaans omdat de upstream Realtek-build-vlaggen hem
hadden uitgeschakeld. Negeer 'm of bouw de driver opnieuw met het
bijbehorende `CONFIG_*`-symbool aan.

**De Module Herladen-knop loopt vast**

`rmmod` blokkeert. Meestal omdat NetworkManager of `wpa_supplicant`
de interface nog vasthoudt. Stop ze, probeer opnieuw:

```bash
sudo systemctl stop NetworkManager wpa_supplicant
```

Patch 0007 in deze fork maakt `rmmod` bestand tegen die race — het
unload-pad keert in minder dan 200 ms terug, ook met een UP
interface — maar externe diensten die het apparaat opnieuw proberen
te claimen kunnen een schone reload alsnog vertragen.
