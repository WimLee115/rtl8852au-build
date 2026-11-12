// ─── i18n ──────────────────────────────────────────────────────────────
const I18N = {
    en: {
        'status.loading': 'Loading...',
        'status.driver_off': 'Driver not loaded',
        'status.connected': 'Connected',
        'status.disconnected': 'Not connected',
        'status.none': 'None',
        'tab.overview': 'Overview', 'tab.networks': 'Networks',
        'tab.settings': 'Settings', 'tab.tests': 'Tests', 'tab.advanced': 'Advanced',
        'card.adapter': 'Adapter Info', 'card.connection': 'Connection',
        'card.stats': 'Statistics', 'card.driver': 'Driver Info',
        'card.scan': 'Available networks', 'card.connect': 'Connect manually',
        'card.iface': 'Interface Settings', 'card.tests': 'Driver Test Suite',
        'btn.scan': 'Scan', 'btn.connect': 'Connect', 'btn.disconnect': 'Disconnect',
        'btn.apply': 'Apply', 'btn.runtests': 'Run tests',
        'btn.saveapply': 'Save & Apply', 'btn.resetdefault': 'Reset to default',
        'btn.reloadmod': 'Reload module', 'btn.quickconnect': 'Connect',
        'th.ssid': 'SSID', 'th.bssid': 'BSSID', 'th.signal': 'Signal',
        'th.freq': 'Freq', 'th.security': 'Security',
        'label.password': 'Password', 'label.txpower': 'TX Power (dBm)',
        'label.powersave': 'Power Save', 'label.interface': 'Interface',
        'label.mac': 'MAC address', 'label.ip': 'IP address',
        'label.status': 'Status', 'label.mtu': 'MTU',
        'label.usbspeed': 'USB speed', 'label.usbdev': 'USB device',
        'label.signal': 'Signal', 'label.freq': 'Frequency',
        'label.txbitrate': 'TX bitrate', 'label.module': 'Module',
        'label.driver': 'Driver', 'label.kernel': 'Kernel',
        'label.srcversion': 'Srcversion', 'label.version': 'Version',
        'label.current': 'Current value (active)',
        'label.pending': 'Saved (waiting for restart)',
        'label.property': 'Property',
        'opt.off': 'Off', 'opt.on': 'On', 'opt.auto': 'Auto',
        'opt.auto_efuse': 'Auto (Efuse)', 'opt.none': 'None',
        'opt.minimal': 'Minimal', 'opt.maximal': 'Maximal',
        'opt.normal': 'Normal', 'opt.level2': 'Level 2',
        'opt.clockgating': 'Clock Gating', 'opt.powergating': 'Power Gating',
        'opt.nochange': 'No change', 'opt.only24': '2.4 GHz only',
        'opt.only5': '5 GHz only', 'opt.dualband': 'Dual-band',
        'opt.both_bands': 'Both bands',
        'opt.1stream': '1 stream', 'opt.2streams': '2 streams',
        'opt.error': 'Error', 'opt.warning': 'Warning', 'opt.notice': 'Notice',
        'opt.info': 'Info', 'opt.debug': 'Debug',
        'opt.usb3': 'USB 3.0', 'opt.usb2': 'USB 2.0',
        'opt.hidden': '(Hidden)',
        'stat.tx_data': 'TX Data', 'stat.rx_data': 'RX Data',
        'stat.tx_pkts': 'TX Packets', 'stat.rx_pkts': 'RX Packets',
        'stat.tx_err': 'TX Errors', 'stat.rx_err': 'RX Errors',
        'stat.tx_drop': 'TX Dropped', 'stat.rx_drop': 'RX Dropped',
        'ph.network': 'Network name',
        'ph.password': 'Password (leave blank for open)',
        'scan.click': 'Click Scan...',
        'scan.scanning': 'Scanning...',
        'scan.found': 'networks found',
        'scan.none': 'No networks found',
        'scan.error': 'Scan error',
        'scan.errorfmt': 'Error: ',
        'tests.click': 'Click "Run tests" to start the suite...',
        'tests.running': 'Running tests...',
        'tests.busy': 'Busy...',
        'tests.nooutput': 'No output',
        'tests.error': 'Error running tests',
        'tests.passed': 'passed',
        'tests.failed': 'failed',
        'tests.errors': 'errors',
        'tests.skipped': 'skipped',
        'conn.notconnected': 'Not connected to a network',
        'toast.enterssid': 'Enter an SSID',
        'toast.connected': 'Connected to ',
        'toast.connectfail': 'Connect failed',
        'toast.connecterr': 'Error connecting',
        'toast.disconnected': 'Disconnected',
        'toast.disconnerr': 'Error disconnecting',
        'toast.applied': 'Settings applied',
        'toast.applyerr': 'Error applying settings',
        'toast.nochanges': 'No changes to save',
        'toast.saved': 'Settings saved.',
        'toast.savedrestart': 'Settings saved. Module restart needed.',
        'toast.saveerr': 'Error saving',
        'toast.resetlocal': 'Local changes discarded',
        'toast.reloading': 'Reloading module...',
        'toast.reloaded': 'Module reloaded successfully',
        'toast.reloadfail': 'Reload failed',
        'toast.reloaderr': 'Error reloading',
        'adv.pickcat': 'Select a category and property to configure.',
        'adv.pickprop': 'Select a property to configure.',
        'adv.unavailable': 'Not available — this parameter is not compiled into the current module.',
        'adv.modulerestart': 'Module parameter — restart needed',
        'adv.reloadconfirm': 'Reload module?\n\nThe WiFi connection will be briefly interrupted. The adapter will reinitialise with the saved settings.\n\nContinue?',
        'adv.pending_1': ' unsaved change. Click "Save & Apply" to save, then "Reload module" to activate.',
        'adv.pending_n': ' unsaved changes. Click "Save & Apply" to save, then "Reload module" to activate.',
        'adv.pending_saved': 'There are saved changes that require a module restart. Click "Reload module" to activate.',
        'adv.cat.wireless': 'Wireless Mode',
        'adv.cat.channel': 'Channel & Bandwidth',
        'adv.cat.power': 'Power Management',
        'adv.cat.performance': 'Performance',
        'adv.cat.antenna': 'Antenna & Beamforming',
        'adv.cat.roaming': 'Roaming & Connection',
        'adv.cat.debug': 'Debug & Advanced',
        'card.trends': 'Trends (last 60 min)',
        'trend.signal': 'Signal',
        'trend.bitrate': 'TX bitrate',
        'trend.throughput': 'RX throughput',
        'trend.errors': 'Errors (Δ)',
        'trend.nodata': 'no data yet',
        'kbd.title': 'Keyboard shortcuts',
        'kbd.tab1': 'Overview tab', 'kbd.tab2': 'Networks tab',
        'kbd.tab3': 'Settings tab', 'kbd.tab4': 'Tests tab',
        'kbd.tab5': 'Advanced tab', 'kbd.scan': 'Scan networks',
        'kbd.refresh': 'Refresh status', 'kbd.theme': 'Toggle theme',
        'kbd.lang': 'Toggle language', 'kbd.help': 'Show this help',
        'footer.by': 'by',
        'footer.and': '& the Linux community',
        'card.spectrum': 'Channel usage',
        'spectrum.click': 'Click Scan to load — auto-refresh every 30 s.',
        'spectrum.ch24': '(channels 1–14)',
        'spectrum.ch5': '(channels 36–165)',
        'spectrum.nodata': 'no scan data yet',
        'spectrum.summary': 'aps across {n} channels',
        'tab.monitor': 'Monitor',
        'card.monitor': 'Monitor mode',
        'card.channelpicker': 'Channel selection',
        'card.capture': 'Frame capture',
        'monitor.warning': 'Monitor mode requires the interface to be unmanaged by NetworkManager / wpa_supplicant. Run:  sudo nmcli device set wlanX managed no  &&  sudo systemctl stop wpa_supplicant',
        'monitor.iface': 'Interface',
        'monitor.mode': 'Mode',
        'monitor.channel': 'Channel',
        'monitor.enable': 'Enable monitor',
        'monitor.disable': 'Back to managed',
        'monitor.channelpick': 'Channel',
        'btn.capture_start': 'Start capture',
        'btn.capture_stop': 'Stop capture',
        'btn.pcap': 'Download .pcap',
        'ph.framefilter': 'Filter (e.g. Beacon, Probe)',
        'frame.time': 'Time',
        'frame.type': 'Type',
        'frame.src': 'Source',
        'frame.dst': 'Dest',
        'frame.ssid': 'SSID',
        'frame.rssi': 'RSSI',
        'frame.empty': 'Start a capture to see frames here.',
        'frame.nomatch': 'No frames matched the filter.',
        'monitor.cap_running': 'capturing — {n} frames',
        'monitor.cap_stopped': '{n} frames captured',
        'toast.mon_enabled': 'Monitor mode active',
        'toast.mon_disabled': 'Back to managed mode',
        'toast.mon_fail': 'Failed to switch mode — check NetworkManager / wpa_supplicant',
        'toast.cap_started': 'Capture started',
        'toast.cap_stopped': 'Capture stopped',
        'toast.ch_set': 'Channel set to {n}',
        'toast.ch_fail': 'Channel change rejected',
    },
    nl: {
        'status.loading': 'Laden...',
        'status.driver_off': 'Driver niet geladen',
        'status.connected': 'Verbonden',
        'status.disconnected': 'Niet verbonden',
        'status.none': 'Geen',
        'tab.overview': 'Overzicht', 'tab.networks': 'Netwerken',
        'tab.settings': 'Instellingen', 'tab.tests': 'Tests', 'tab.advanced': 'Geavanceerd',
        'card.adapter': 'Adapter Info', 'card.connection': 'Verbinding',
        'card.stats': 'Statistieken', 'card.driver': 'Driver Info',
        'card.scan': 'Beschikbare Netwerken', 'card.connect': 'Handmatig Verbinden',
        'card.iface': 'Interface Instellingen', 'card.tests': 'Driver Test Suite',
        'btn.scan': 'Scannen', 'btn.connect': 'Verbinden', 'btn.disconnect': 'Verbreken',
        'btn.apply': 'Toepassen', 'btn.runtests': 'Tests Draaien',
        'btn.saveapply': 'Opslaan & Toepassen', 'btn.resetdefault': 'Standaard Herstellen',
        'btn.reloadmod': 'Module Herladen', 'btn.quickconnect': 'Verbind',
        'th.ssid': 'SSID', 'th.bssid': 'BSSID', 'th.signal': 'Signaal',
        'th.freq': 'Freq', 'th.security': 'Beveiliging',
        'label.password': 'Wachtwoord', 'label.txpower': 'TX Power (dBm)',
        'label.powersave': 'Power Save', 'label.interface': 'Interface',
        'label.mac': 'MAC Adres', 'label.ip': 'IP Adres',
        'label.status': 'Status', 'label.mtu': 'MTU',
        'label.usbspeed': 'USB Snelheid', 'label.usbdev': 'USB Apparaat',
        'label.signal': 'Signaal', 'label.freq': 'Frequentie',
        'label.txbitrate': 'TX Bitrate', 'label.module': 'Module',
        'label.driver': 'Driver', 'label.kernel': 'Kernel',
        'label.srcversion': 'Srcversion', 'label.version': 'Versie',
        'label.current': 'Huidige waarde (actief)',
        'label.pending': 'Opgeslagen (wacht op herstart)',
        'label.property': 'Eigenschap',
        'opt.off': 'Uit', 'opt.on': 'Aan', 'opt.auto': 'Auto',
        'opt.auto_efuse': 'Auto (Efuse)', 'opt.none': 'Geen',
        'opt.minimal': 'Minimaal', 'opt.maximal': 'Maximaal',
        'opt.normal': 'Normaal', 'opt.level2': 'Level 2',
        'opt.clockgating': 'Clock Gating', 'opt.powergating': 'Power Gating',
        'opt.nochange': 'Geen wijziging', 'opt.only24': 'Alleen 2.4 GHz',
        'opt.only5': 'Alleen 5 GHz', 'opt.dualband': 'Dual-band',
        'opt.both_bands': 'Beide banden',
        'opt.1stream': '1 Stream', 'opt.2streams': '2 Streams',
        'opt.error': 'Error', 'opt.warning': 'Warning', 'opt.notice': 'Notice',
        'opt.info': 'Info', 'opt.debug': 'Debug',
        'opt.usb3': 'USB 3.0', 'opt.usb2': 'USB 2.0',
        'opt.hidden': '(Verborgen)',
        'stat.tx_data': 'TX Data', 'stat.rx_data': 'RX Data',
        'stat.tx_pkts': 'TX Pakketten', 'stat.rx_pkts': 'RX Pakketten',
        'stat.tx_err': 'TX Fouten', 'stat.rx_err': 'RX Fouten',
        'stat.tx_drop': 'TX Dropped', 'stat.rx_drop': 'RX Dropped',
        'ph.network': 'Netwerknaam',
        'ph.password': 'Wachtwoord (leeg voor open)',
        'scan.click': 'Klik op Scannen...',
        'scan.scanning': 'Scannen...',
        'scan.found': 'netwerken gevonden',
        'scan.none': 'Geen netwerken gevonden',
        'scan.error': 'Fout bij scannen',
        'scan.errorfmt': 'Fout: ',
        'tests.click': 'Klik op "Tests Draaien" om de testsuite te starten...',
        'tests.running': 'Tests worden uitgevoerd...',
        'tests.busy': 'Bezig...',
        'tests.nooutput': 'Geen output',
        'tests.error': 'Fout bij uitvoeren tests',
        'tests.passed': 'geslaagd',
        'tests.failed': 'gefaald',
        'tests.errors': 'fouten',
        'tests.skipped': 'overgeslagen',
        'conn.notconnected': 'Niet verbonden met een netwerk',
        'toast.enterssid': 'Voer een SSID in',
        'toast.connected': 'Verbonden met ',
        'toast.connectfail': 'Verbinden mislukt',
        'toast.connecterr': 'Fout bij verbinden',
        'toast.disconnected': 'Verbinding verbroken',
        'toast.disconnerr': 'Fout bij verbreken',
        'toast.applied': 'Instellingen toegepast',
        'toast.applyerr': 'Fout bij toepassen',
        'toast.nochanges': 'Geen wijzigingen om op te slaan',
        'toast.saved': 'Instellingen opgeslagen.',
        'toast.savedrestart': 'Instellingen opgeslagen. Module herstart nodig.',
        'toast.saveerr': 'Fout bij opslaan',
        'toast.resetlocal': 'Lokale wijzigingen gewist',
        'toast.reloading': 'Module wordt herladen...',
        'toast.reloaded': 'Module succesvol herladen',
        'toast.reloadfail': 'Herladen mislukt',
        'toast.reloaderr': 'Fout bij herladen',
        'adv.pickcat': 'Selecteer een categorie en eigenschap om te configureren.',
        'adv.pickprop': 'Selecteer een eigenschap om te configureren.',
        'adv.unavailable': 'Niet beschikbaar — deze parameter is niet gecompileerd in de huidige module.',
        'adv.modulerestart': 'Module parameter — herstart nodig',
        'adv.reloadconfirm': 'Module herladen?\n\nDe WiFi-verbinding wordt tijdelijk verbroken. De adapter wordt opnieuw geïnitialiseerd met de opgeslagen instellingen.\n\nDoorgaan?',
        'adv.pending_1': ' onopgeslagen wijziging. Klik "Opslaan & Toepassen" om op te slaan, daarna "Module Herladen" om te activeren.',
        'adv.pending_n': ' onopgeslagen wijzigingen. Klik "Opslaan & Toepassen" om op te slaan, daarna "Module Herladen" om te activeren.',
        'adv.pending_saved': 'Er zijn opgeslagen wijzigingen die een module herstart vereisen. Klik "Module Herladen" om te activeren.',
        'adv.cat.wireless': 'Draadloze Modus',
        'adv.cat.channel': 'Kanaal & Bandbreedte',
        'adv.cat.power': 'Energiebeheer',
        'adv.cat.performance': 'Prestaties',
        'adv.cat.antenna': 'Antenne & Beamforming',
        'adv.cat.roaming': 'Roaming & Verbinding',
        'adv.cat.debug': 'Debug & Geavanceerd',
        'card.trends': 'Trends (laatste 60 min)',
        'trend.signal': 'Signaal',
        'trend.bitrate': 'TX bitrate',
        'trend.throughput': 'RX doorvoer',
        'trend.errors': 'Fouten (Δ)',
        'trend.nodata': 'nog geen data',
        'kbd.title': 'Sneltoetsen',
        'kbd.tab1': 'Overzicht-tab', 'kbd.tab2': 'Netwerken-tab',
        'kbd.tab3': 'Instellingen-tab', 'kbd.tab4': 'Tests-tab',
        'kbd.tab5': 'Geavanceerd-tab', 'kbd.scan': 'Netwerken scannen',
        'kbd.refresh': 'Status verversen', 'kbd.theme': 'Thema wisselen',
        'kbd.lang': 'Taal wisselen', 'kbd.help': 'Deze help tonen',
        'footer.by': 'door',
        'footer.and': '& de Linux-community',
        'card.spectrum': 'Kanaal-bezetting',
        'spectrum.click': 'Klik op Scannen om te laden — automatisch verversen elke 30 s.',
        'spectrum.ch24': '(kanalen 1–14)',
        'spectrum.ch5': '(kanalen 36–165)',
        'spectrum.nodata': 'nog geen scan-data',
        'spectrum.summary': 'APs verdeeld over {n} kanalen',
        'tab.monitor': 'Monitor',
        'card.monitor': 'Monitor-modus',
        'card.channelpicker': 'Kanaal-keuze',
        'card.capture': 'Frame-capture',
        'monitor.warning': 'Monitor-modus vereist dat de interface niet door NetworkManager / wpa_supplicant wordt beheerd. Draai:  sudo nmcli device set wlanX managed no  &&  sudo systemctl stop wpa_supplicant',
        'monitor.iface': 'Interface',
        'monitor.mode': 'Modus',
        'monitor.channel': 'Kanaal',
        'monitor.enable': 'Monitor inschakelen',
        'monitor.disable': 'Terug naar managed',
        'monitor.channelpick': 'Kanaal',
        'btn.capture_start': 'Capture starten',
        'btn.capture_stop': 'Capture stoppen',
        'btn.pcap': '.pcap downloaden',
        'ph.framefilter': 'Filter (bijv. Beacon, Probe)',
        'frame.time': 'Tijd',
        'frame.type': 'Type',
        'frame.src': 'Bron',
        'frame.dst': 'Bestemming',
        'frame.ssid': 'SSID',
        'frame.rssi': 'RSSI',
        'frame.empty': 'Start een capture om hier frames te zien.',
        'frame.nomatch': 'Geen frames matchen het filter.',
        'monitor.cap_running': 'capturet — {n} frames',
        'monitor.cap_stopped': '{n} frames opgevangen',
        'toast.mon_enabled': 'Monitor-modus actief',
        'toast.mon_disabled': 'Terug naar managed-modus',
        'toast.mon_fail': 'Modus wisselen mislukt — controleer NetworkManager / wpa_supplicant',
        'toast.cap_started': 'Capture gestart',
        'toast.cap_stopped': 'Capture gestopt',
        'toast.ch_set': 'Kanaal ingesteld op {n}',
        'toast.ch_fail': 'Kanaal-wijziging afgewezen',
    }
};

let LANG = localStorage.getItem('rtw_lang')
        || (navigator.language && navigator.language.toLowerCase().startsWith('nl') ? 'nl' : 'en');
let THEME = localStorage.getItem('rtw_theme') || 'dark';

function t(k) { return (I18N[LANG] && I18N[LANG][k]) || I18N.en[k] || k; }

// Escape a value for HTML text or a quoted attribute. Every server-supplied
// value that reaches innerHTML goes through this: much of it comes from the
// air or the USB bus — SSIDs and monitor-mode frame lines are whatever nearby
// transmitters broadcast, the USB product string is whatever the device
// reports — and a 32-byte SSID is room enough for `<img src=x onerror=…>` in
// a page that drives a root process.
function esc(v) {
    return String(v ?? '').replace(/[&<>"'`]/g, c => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;', '`': '&#96;',
    })[c]);
}

function applyTranslations() {
    document.documentElement.setAttribute('lang', LANG);
    document.querySelectorAll('[data-i18n]').forEach(el => {
        el.textContent = t(el.dataset.i18n);
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        el.placeholder = t(el.dataset.i18nPlaceholder);
    });
    document.querySelectorAll('.lang-btn[data-lang]').forEach(b => {
        b.classList.toggle('active', b.dataset.lang === LANG);
    });
    document.querySelectorAll('.lang-btn[data-theme-btn]').forEach(b => {
        b.classList.toggle('active', b.dataset.themeBtn === THEME);
    });
}

function setLanguage(lang) {
    if (!I18N[lang]) return;
    LANG = lang;
    localStorage.setItem('rtw_lang', lang);
    applyTranslations();
    refreshStatus();
    refreshDriverInfo();
    if (advLoaded) {
        renderAdvCategories();
        if (advSelectedCat) {
            renderAdvProperties(advSelectedCat);
            if (advSelectedParam) renderAdvEditor(advSelectedCat, advSelectedParam);
        }
        updatePendingBanner(Object.keys(advChanges).length > 0);
    }
    drawAllTrends();
}

function setTheme(theme) {
    if (theme !== 'light' && theme !== 'dark') return;
    THEME = theme;
    localStorage.setItem('rtw_theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
    applyTranslations();
    drawAllTrends();
}

function toggleKbdHelp() {
    document.getElementById('kbd-overlay').classList.toggle('open');
}

document.addEventListener('keydown', e => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const tabs = ['overview','networks','settings','tests','advanced'];
    if (e.key >= '1' && e.key <= '5') { switchTab(tabs[+e.key - 1]); }
    else if (e.key === '/') { e.preventDefault(); switchTab('networks'); doScan(); }
    else if (e.key === 'r') { refreshStatus(); refreshDriverInfo(); refreshTrends(); }
    else if (e.key === 't') { setTheme(THEME === 'dark' ? 'light' : 'dark'); }
    else if (e.key === 'l') { setLanguage(LANG === 'en' ? 'nl' : 'en'); }
    else if (e.key === '?' || (e.shiftKey && e.key === '/')) { toggleKbdHelp(); }
    else if (e.key === 'Escape') { document.getElementById('kbd-overlay').classList.remove('open'); }
});

// ── Trend sparklines ───────────────────────────────────────────────────
let TRENDS = { samples: [] };

function themeColor(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function drawSparkline(canvas, values, opts) {
    if (!canvas) return;
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.max(rect.width * dpr, 100);
    canvas.height = rect.height * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    const w = rect.width, h = rect.height;
    ctx.clearRect(0, 0, w, h);
    const clean = values.filter(v => v !== null && v !== undefined && !Number.isNaN(v));
    if (clean.length < 2) {
        ctx.fillStyle = themeColor('--text-dim');
        ctx.font = '11px sans-serif';
        ctx.fillText(t('trend.nodata'), 4, h / 2 + 4);
        return;
    }
    let min = Math.min(...clean), max = Math.max(...clean);
    if (opts && opts.minClamp !== undefined) min = Math.min(min, opts.minClamp);
    if (opts && opts.maxClamp !== undefined) max = Math.max(max, opts.maxClamp);
    const range = (max - min) || 1;
    const pad = 2;
    const stepX = (w - 2 * pad) / Math.max(values.length - 1, 1);
    // Fill under the line for nicer visual weight.
    ctx.beginPath();
    ctx.moveTo(pad, h - pad);
    values.forEach((v, i) => {
        if (v === null || v === undefined || Number.isNaN(v)) return;
        const x = pad + i * stepX;
        const y = h - pad - ((v - min) / range) * (h - 2 * pad);
        ctx.lineTo(x, y);
    });
    ctx.lineTo(w - pad, h - pad);
    ctx.closePath();
    ctx.fillStyle = (opts && opts.fill) || themeColor('--accent') + '22';
    ctx.fill();
    // Stroke on top.
    ctx.beginPath();
    let started = false;
    values.forEach((v, i) => {
        if (v === null || v === undefined || Number.isNaN(v)) return;
        const x = pad + i * stepX;
        const y = h - pad - ((v - min) / range) * (h - 2 * pad);
        if (!started) { ctx.moveTo(x, y); started = true; } else { ctx.lineTo(x, y); }
    });
    ctx.strokeStyle = (opts && opts.stroke) || themeColor('--accent');
    ctx.lineWidth = 1.5;
    ctx.stroke();
}

function fmtBytesPerSec(bps) {
    if (bps == null || Number.isNaN(bps)) return '–';
    if (bps < 1024) return bps.toFixed(0) + ' B/s';
    if (bps < 1024 * 1024) return (bps / 1024).toFixed(1) + ' KB/s';
    return (bps / (1024 * 1024)).toFixed(2) + ' MB/s';
}

function drawAllTrends() {
    const samples = TRENDS.samples || [];
    const signals = samples.map(s => s.signal);
    const bitrates = samples.map(s => s.bitrate);
    // Throughput is the per-sample delta in rx_bytes / dt seconds.
    const throughputs = samples.map((s, i) => {
        if (i === 0) return null;
        const dt = s.t - samples[i - 1].t;
        if (dt <= 0) return null;
        return (s.rx_bytes - samples[i - 1].rx_bytes) / dt;
    });
    const errorDeltas = samples.map((s, i) => {
        if (i === 0) return 0;
        return Math.max(0, s.errors - samples[i - 1].errors);
    });

    drawSparkline(document.getElementById('trend-signal'), signals, {});
    drawSparkline(document.getElementById('trend-bitrate'), bitrates, {minClamp: 0});
    drawSparkline(document.getElementById('trend-throughput'), throughputs, {minClamp: 0});
    drawSparkline(document.getElementById('trend-errors'), errorDeltas,
                  {minClamp: 0, stroke: '#dc2626', fill: '#dc262633'});

    const last = samples[samples.length - 1] || {};
    document.getElementById('trend-signal-val').textContent =
        last.signal != null ? last.signal + ' dBm' : '–';
    document.getElementById('trend-bitrate-val').textContent =
        last.bitrate != null ? last.bitrate.toFixed(0) + ' Mbps' : '–';
    const lastTp = throughputs[throughputs.length - 1];
    document.getElementById('trend-throughput-val').textContent = fmtBytesPerSec(lastTp);
    const recentErrors = errorDeltas.slice(-12).reduce((a, b) => a + b, 0);
    document.getElementById('trend-errors-val').textContent = String(recentErrors);
}

async function refreshTrends() {
    try {
        const r = await fetch('/api/history');
        const d = await r.json();
        TRENDS = d;
        drawAllTrends();
    } catch (e) {
        console.error('History fetch failed:', e);
    }
}
window.addEventListener('resize', () => drawAllTrends());

// ── Spectrum view ──────────────────────────────────────────────────────
const SPECTRUM_24_CHANNELS = [1,2,3,4,5,6,7,8,9,10,11,12,13,14];
const SPECTRUM_5_CHANNELS  = [36,40,44,48,52,56,60,64,100,104,108,112,116,120,124,128,132,136,140,144,149,153,157,161,165];

let SPECTRUM_DATA = null;

function drawSpectrumBand(canvasId, channels, slots) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.max(rect.width * dpr, 200);
    canvas.height = rect.height * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    const w = rect.width, h = rect.height;
    ctx.clearRect(0, 0, w, h);

    const margin = {top: 6, right: 8, bottom: 22, left: 28};
    const innerW = w - margin.left - margin.right;
    const innerH = h - margin.top - margin.bottom;
    const slotMap = new Map();
    (slots || []).forEach(s => slotMap.set(s.channel, s));
    const colWidth = innerW / channels.length;

    // Y-axis: signal range -90..-20 dBm
    const yMin = -90, yMax = -20;
    function yFor(dbm) {
        if (dbm == null) return null;
        const clamped = Math.max(yMin, Math.min(yMax, dbm));
        return margin.top + innerH - ((clamped - yMin) / (yMax - yMin)) * innerH;
    }

    // Background grid + y-axis labels
    ctx.strokeStyle = themeColor('--border');
    ctx.fillStyle = themeColor('--text-dim');
    ctx.font = '10px sans-serif';
    ctx.lineWidth = 1;
    [-30, -50, -70, -90].forEach(db => {
        const y = yFor(db);
        ctx.beginPath();
        ctx.moveTo(margin.left, y);
        ctx.lineTo(w - margin.right, y);
        ctx.stroke();
        ctx.fillText(db + ' dBm', 2, y + 3);
    });

    // Bars per channel
    channels.forEach((ch, idx) => {
        const x = margin.left + idx * colWidth + colWidth * 0.15;
        const barW = colWidth * 0.7;
        const slot = slotMap.get(ch);
        if (slot && slot.max_signal != null) {
            const y = yFor(slot.max_signal);
            const colour = slot.ap_count >= 3
                ? '#dc2626'
                : slot.ap_count === 2 ? '#f59e0b' : themeColor('--accent');
            ctx.fillStyle = colour;
            ctx.fillRect(x, y, barW, margin.top + innerH - y);
            // AP-count badge above the bar
            ctx.fillStyle = themeColor('--text');
            ctx.font = 'bold 10px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(slot.ap_count, x + barW / 2, y - 3);
        }
        // X-axis label
        ctx.fillStyle = themeColor('--text-dim');
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(ch, x + barW / 2, h - 6);
    });
    ctx.textAlign = 'start';
}

function drawSpectrum() {
    if (!SPECTRUM_DATA) {
        ['spectrum-24', 'spectrum-5'].forEach(id => {
            const c = document.getElementById(id);
            if (c) {
                const ctx = c.getContext('2d');
                const rect = c.getBoundingClientRect();
                c.width = rect.width; c.height = rect.height;
                ctx.fillStyle = themeColor('--text-dim');
                ctx.font = '12px sans-serif';
                ctx.fillText(t('spectrum.nodata'), 12, rect.height / 2 + 4);
            }
        });
        return;
    }
    drawSpectrumBand('spectrum-24', SPECTRUM_24_CHANNELS, SPECTRUM_DATA.bands['2.4']);
    drawSpectrumBand('spectrum-5',  SPECTRUM_5_CHANNELS,  SPECTRUM_DATA.bands['5']);
    const usedChannels =
        ((SPECTRUM_DATA.bands['2.4'] || []).length + (SPECTRUM_DATA.bands['5'] || []).length);
    document.getElementById('spectrum-summary').textContent =
        SPECTRUM_DATA.total_aps + ' ' + t('spectrum.summary').replace('{n}', usedChannels);
}

async function refreshSpectrum() {
    try {
        const r = await fetch('/api/spectrum');
        if (!r.ok) return;
        SPECTRUM_DATA = await r.json();
        drawSpectrum();
    } catch (e) { /* leave stale data */ }
}

window.addEventListener('resize', () => drawSpectrum());

// ── Monitor mode ───────────────────────────────────────────────────────
let MONITOR_INFO = null;
let MONITOR_POLL = null;
let MONITOR_FRAMES_CACHE = [];

function populateChannelSelect(info) {
    const sel = document.getElementById('mon-channel-select');
    if (!sel || !info) return;
    const current = sel.value;
    sel.innerHTML = '<option value="">--</option>';
    const optgroup24 = document.createElement('optgroup');
    optgroup24.label = '2.4 GHz';
    info.channels_24.forEach(ch => {
        const opt = document.createElement('option');
        opt.value = ch; opt.textContent = ch;
        if (info.channel === ch) opt.selected = true;
        optgroup24.appendChild(opt);
    });
    sel.appendChild(optgroup24);
    const optgroup5 = document.createElement('optgroup');
    optgroup5.label = '5 GHz';
    info.channels_5.forEach(ch => {
        const opt = document.createElement('option');
        opt.value = ch; opt.textContent = ch;
        if (info.channel === ch) opt.selected = true;
        optgroup5.appendChild(opt);
    });
    sel.appendChild(optgroup5);
    if (current && !info.channel) sel.value = current;
}

async function refreshMonitorStatus() {
    try {
        const r = await fetch('/api/monitor/status');
        if (!r.ok) return;
        MONITOR_INFO = await r.json();
        document.getElementById('mon-iface').textContent = MONITOR_INFO.interface || '–';
        document.getElementById('mon-mode').textContent = MONITOR_INFO.type || '–';
        document.getElementById('mon-channel').textContent = MONITOR_INFO.channel || '–';
        populateChannelSelect(MONITOR_INFO);

        const startBtn = document.getElementById('btn-capture-start');
        const stopBtn  = document.getElementById('btn-capture-stop');
        const pcapBtn  = document.getElementById('btn-pcap');
        startBtn.disabled = !!MONITOR_INFO.capturing || MONITOR_INFO.type !== 'monitor';
        stopBtn.disabled  = !MONITOR_INFO.capturing;
        pcapBtn.disabled  = !MONITOR_INFO.pcap_available;

        const stats = document.getElementById('capture-stats');
        if (MONITOR_INFO.capturing) {
            stats.textContent = t('monitor.cap_running').replace('{n}', MONITOR_INFO.frame_count);
        } else if (MONITOR_INFO.frame_count > 0) {
            stats.textContent = t('monitor.cap_stopped').replace('{n}', MONITOR_INFO.frame_count);
        } else {
            stats.textContent = '';
        }
    } catch (e) { /* leave stale */ }
}

async function monitorEnable() {
    const ch = document.getElementById('mon-channel-select').value || null;
    try {
        const r = await fetch('/api/monitor/enable', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({channel: ch})
        });
        const d = await r.json();
        if (d.success) {
            showToast(t('toast.mon_enabled'), true);
            refreshMonitorStatus();
        } else {
            showToast(d.error || t('toast.mon_fail'), false);
        }
    } catch (e) { showToast(t('toast.mon_fail'), false); }
}

async function monitorDisable() {
    try {
        const r = await fetch('/api/monitor/disable', {method: 'POST'});
        const d = await r.json();
        if (d.success) {
            showToast(t('toast.mon_disabled'), true);
            refreshMonitorStatus();
        } else {
            showToast(d.error || t('toast.mon_fail'), false);
        }
    } catch (e) { showToast(t('toast.mon_fail'), false); }
}

async function monitorSetChannel() {
    const ch = document.getElementById('mon-channel-select').value;
    if (!ch) return;
    try {
        const r = await fetch('/api/monitor/channel', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({channel: ch})
        });
        const d = await r.json();
        if (d.success) {
            showToast(t('toast.ch_set').replace('{n}', ch), true);
            refreshMonitorStatus();
        } else {
            showToast(d.error || t('toast.ch_fail'), false);
        }
    } catch (e) { showToast(t('toast.ch_fail'), false); }
}

async function captureStart() {
    try {
        const r = await fetch('/api/monitor/capture/start', {method: 'POST'});
        const d = await r.json();
        if (d.success) {
            showToast(t('toast.cap_started'), true);
            refreshMonitorStatus();
            refreshFrames();
        } else {
            showToast(d.error || 'Capture failed', false);
        }
    } catch (e) { showToast('Capture failed', false); }
}

async function captureStop() {
    try {
        await fetch('/api/monitor/capture/stop', {method: 'POST'});
        showToast(t('toast.cap_stopped'), true);
        refreshMonitorStatus();
        refreshFrames();
    } catch (e) {}
}

function downloadPcap() {
    // Force a fresh request — the underlying file is rewritten on each
    // capture run.
    window.location.href = '/api/monitor/pcap?_t=' + Date.now();
}

async function refreshFrames() {
    try {
        const r = await fetch('/api/monitor/frames');
        if (!r.ok) return;
        const d = await r.json();
        MONITOR_FRAMES_CACHE = d.frames || [];
        renderFrames();
    } catch (e) {}
}

function renderFrames() {
    const filterRaw = (document.getElementById('frame-filter') || {}).value || '';
    const filter = filterRaw.toLowerCase();
    const tbody = document.getElementById('frame-list');
    if (!tbody) return;
    const frames = MONITOR_FRAMES_CACHE.filter(f => {
        if (!filter) return true;
        return ((f.type || '') + ' ' + (f.src || '') + ' ' + (f.dst || '') +
                ' ' + (f.ssid || '') + ' ' + (f.raw || '')).toLowerCase().includes(filter);
    });
    if (frames.length === 0) {
        const empty = MONITOR_FRAMES_CACHE.length === 0 ? t('frame.empty') : t('frame.nomatch');
        tbody.innerHTML = `<tr><td colspan="6">${empty}</td></tr>`;
        return;
    }
    // Newest first.
    const rows = frames.slice().reverse().slice(0, 200).map(f => {
        const ts = new Date(f.t * 1000).toLocaleTimeString();
        return `<tr>
            <td style="font-family:monospace;font-size:0.8rem;">${esc(ts)}</td>
            <td>${esc(f.type || '?')}</td>
            <td style="font-family:monospace;font-size:0.8rem;">${esc(f.src)}</td>
            <td style="font-family:monospace;font-size:0.8rem;">${esc(f.dst)}</td>
            <td>${esc(f.ssid)}</td>
            <td>${f.rssi != null ? esc(f.rssi) + ' dBm' : ''}</td>
        </tr>`;
    });
    tbody.innerHTML = rows.join('');
}

function formatBytes(b) {
    if (b < 1024) return b + ' B';
    if (b < 1048576) return (b/1024).toFixed(1) + ' KB';
    if (b < 1073741824) return (b/1048576).toFixed(1) + ' MB';
    return (b/1073741824).toFixed(2) + ' GB';
}

function signalColor(dbm) {
    if (dbm >= -50) return '#22c55e';
    if (dbm >= -60) return '#84cc16';
    if (dbm >= -70) return '#eab308';
    if (dbm >= -80) return '#f97316';
    return '#ef4444';
}

function signalPercent(dbm) {
    return Math.max(0, Math.min(100, (dbm + 100) * 2));
}

function showToast(msg, ok) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.className = 'toast ' + (ok ? 'toast-ok' : 'toast-err');
    t.style.opacity = '1';
    setTimeout(() => t.style.opacity = '0', 3000);
}

function switchTab(name) {
    document.querySelectorAll('.tab').forEach(el => {
        el.classList.toggle('active', el.dataset.tab === name);
    });
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    if (name === 'advanced' && !advLoaded) loadAdvanced();
    if (name === 'networks') { refreshSpectrum(); }
    if (name === 'monitor') { refreshMonitorStatus(); refreshFrames(); }
}

// refreshStatus() is defined later as a wrapper around applyStatusPayload —
// the legacy polling implementation has been replaced by the SSE stream.

async function refreshDriverInfo() {
    try {
        const r = await fetch('/api/driver');
        const d = await r.json();
        document.getElementById('driver-info').innerHTML = `
            <div class="info-row"><span class="info-label">${t('label.module')}</span><span class="info-value">${esc(d.module_name)}</span></div>
            <div class="info-row"><span class="info-label">${t('label.driver')}</span><span class="info-value">${esc(d.driver_name)}</span></div>
            <div class="info-row"><span class="info-label">${t('label.kernel')}</span><span class="info-value">${esc(d.kernel_version)}</span></div>
            <div class="info-row"><span class="info-label">${t('label.srcversion')}</span><span class="info-value" style="font-size:0.75rem;">${esc(d.srcversion)}</span></div>
            <div class="info-row"><span class="info-label">${t('label.version')}</span><span class="info-value">${esc(d.modinfo?.version || 'N/A')}</span></div>
        `;
    } catch(e) {}
}

async function doScan() {
    document.getElementById('scan-status').innerHTML = '<span class="spinner"></span> ' + t('scan.scanning');
    document.getElementById('network-list').innerHTML = '';
    try {
        const r = await fetch('/api/scan');
        const d = await r.json();
        if (d.error) {
            document.getElementById('scan-status').textContent = t('scan.errorfmt') + d.error;
            return;
        }
        document.getElementById('scan-status').textContent = d.count + ' ' + t('scan.found');
        let html = '';
        for (const n of d.networks) {
            const pct = signalPercent(n.signal);
            const col = signalColor(n.signal);
            html += `<tr>
                <td><strong>${n.ssid ? esc(n.ssid) : t('opt.hidden')}</strong></td>
                <td style="font-family:monospace;font-size:0.8rem;">${esc(n.bssid)}</td>
                <td>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <div style="width:60px;height:6px;background:#334155;border-radius:3px;">
                            <div style="width:${pct}%;height:100%;background:${col};border-radius:3px;"></div>
                        </div>
                        <span style="font-size:0.8rem;">${n.signal !== null ? esc(n.signal) + ' dBm' : '?'}</span>
                    </div>
                </td>
                <td>${esc(n.frequency || '?')} MHz</td>
                <td>${esc(n.security)}</td>
                <td><button class="btn btn-success btn-sm" data-ssid="${esc(n.ssid)}">${t('btn.quickconnect')}</button></td>
            </tr>`;
        }
        const list = document.getElementById('network-list');
        list.innerHTML = html || `<tr><td colspan="6">${t('scan.none')}</td></tr>`;
        // The SSID travels in a data attribute rather than an inline
        // onclick="quickConnect('…')": quoting a broadcast string into
        // JavaScript inside an HTML attribute cannot be done safely by hand.
        list.querySelectorAll('button[data-ssid]').forEach(b =>
            b.addEventListener('click', () => quickConnect(b.dataset.ssid)));
    } catch(e) {
        document.getElementById('scan-status').textContent = t('scan.error');
    }
}

function quickConnect(ssid) {
    document.getElementById('connect-ssid').value = ssid;
    document.getElementById('connect-pass').focus();
}

async function doConnect() {
    const ssid = document.getElementById('connect-ssid').value;
    const pass = document.getElementById('connect-pass').value;
    if (!ssid) { showToast(t('toast.enterssid'), false); return; }

    try {
        const r = await fetch('/api/connect', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ssid, password: pass})
        });
        const d = await r.json();
        if (d.success) {
            showToast(t('toast.connected') + ssid, true);
            refreshStatus();
        } else {
            showToast(d.error || d.warning || t('toast.connectfail'), false);
        }
    } catch(e) {
        showToast(t('toast.connecterr'), false);
    }
}

async function doDisconnect() {
    try {
        await fetch('/api/disconnect', {method: 'POST'});
        showToast(t('toast.disconnected'), true);
        refreshStatus();
    } catch(e) {
        showToast(t('toast.disconnerr'), false);
    }
}

async function applySettings() {
    const data = {
        mtu: parseInt(document.getElementById('set-mtu').value),
        txpower: parseInt(document.getElementById('set-txpower').value),
        power_save: document.getElementById('set-powersave').value === '1'
    };
    try {
        const r = await fetch('/api/ifconfig', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const d = await r.json();
        showToast(t('toast.applied'), true);
        refreshStatus();
    } catch(e) {
        showToast(t('toast.applyerr'), false);
    }
}

// Tracks intervals that should pause while a long-lived blocking
// request (the test runner) is in flight. The dev-server's connection
// pool plus the always-open SSE stream make Firefox drop the test POST
// after a few seconds of inactivity if we keep polling /api/history in
// parallel. Pausing everything for the duration fixes it.
let _LONG_RUN_PAUSED = false;
function withLongRunPause(fn) {
    return async function(...args) {
        const hadStream = STREAM != null;
        _LONG_RUN_PAUSED = true;
        if (hadStream) { try { STREAM.close(); STREAM = null; } catch (_) {} }
        try {
            return await fn.apply(this, args);
        } finally {
            _LONG_RUN_PAUSED = false;
            if (hadStream) startStream();
        }
    };
}

async function _fetchWithRetry(url, opts, attempts) {
    let lastErr;
    for (let i = 0; i < (attempts || 2); i++) {
        try {
            const r = await fetch(url, opts);
            return r;
        } catch (e) {
            lastErr = e;
            if (i < attempts - 1) await new Promise(res => setTimeout(res, 400));
        }
    }
    throw lastErr;
}

const runTests = withLongRunPause(async function _runTests() {
    const btn = document.getElementById('btn-run-tests');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> ' + t('tests.busy');
    document.getElementById('test-output').textContent = t('tests.running');
    document.getElementById('test-summary').textContent = '';

    try {
        const r = await _fetchWithRetry('/api/tests/run', {
            method: 'POST',
            headers: {'Accept': 'application/json'},
            keepalive: false,
        }, 2);
        if (!r.ok) {
            throw new Error('HTTP ' + r.status + ' ' + r.statusText);
        }
        const ct = r.headers.get('content-type') || '';
        if (!ct.includes('json')) {
            throw new Error('Unexpected response type: ' + ct);
        }
        const d = await r.json();

        let html = '';
        if (d.output) {
            // Escape first, then add the markup: test output quotes interface
            // names, scan results and kernel log lines.
            html = esc(d.output)
                .replace(/\.\.\.\s*ok/g, '... <span class="test-pass">OK</span>')
                .replace(/FAIL/g, '<span class="test-fail">FAIL</span>')
                .replace(/ERROR/g, '<span class="test-fail">ERROR</span>');
        }
        document.getElementById('test-output').innerHTML = html || esc(d.stderr) || t('tests.nooutput');

        if (d.report && typeof d.report === 'object') {
            const rp = d.report;
            const ok = (rp.failed | 0) === 0 && (rp.errors | 0) === 0;
            const color = ok ? '#6ee7b7' : '#fca5a5';
            const passed  = rp.passed  != null ? rp.passed  : '?';
            const total   = rp.total   != null ? rp.total   : '?';
            const failed  = rp.failed  != null ? rp.failed  : 0;
            const errors  = rp.errors  != null ? rp.errors  : 0;
            const skipped = rp.skipped != null ? rp.skipped : 0;
            document.getElementById('test-summary').innerHTML =
                `<span style="color:${color};font-size:1.1rem;font-weight:600;">` +
                `${esc(passed)}/${esc(total)} ${t('tests.passed')}</span> | ` +
                `${esc(failed)} ${t('tests.failed')} | ${esc(errors)} ${t('tests.errors')} | ${esc(skipped)} ${t('tests.skipped')}`;
        }
    } catch(e) {
        // Surface the actual error in the UI so it's diagnosable from the
        // dashboard alone — the previous generic "Error running tests"
        // turned every cause into one indistinguishable message.
        console.error('runTests failed:', e);
        document.getElementById('test-output').textContent =
            t('tests.error') + ': ' + (e && e.message ? e.message : String(e));
    }

    btn.disabled = false;
    btn.textContent = t('btn.runtests');
});

// ── Advanced Tab Logic ───────────────────────────────────────────────

let advLoaded = false;
let advData = {};
let advChanges = {};
let advSelectedCat = null;
let advSelectedParam = null;

// All labels and descriptions carry both languages. Helper L() / D() pull
// the active language at render time so a language switch immediately
// re-skins the advanced tab without a refetch.
function L(p) { return (p.label && (p.label[LANG] || p.label.en)) || ''; }
function D(p) { return (p.desc  && (p.desc[LANG]  || p.desc.en))  || ''; }

const ADV_SETTINGS = {
    wireless: {
        labelKey: 'adv.cat.wireless',
        params: {
            rtw_ht_enable:     {
                label: { en: '802.11n (HT)', nl: '802.11n (HT)' },
                desc:  { en: 'Enable or disable 802.11n High Throughput. Required for WiFi 4 speeds above 54 Mbps.',
                         nl: 'Schakel 802.11n High Throughput in of uit. Vereist voor WiFi 4 snelheden boven 54 Mbps.' } },
            rtw_vht_enable:    {
                label: { en: '802.11ac (VHT)', nl: '802.11ac (VHT)' },
                desc:  { en: 'Enable or disable 802.11ac Very High Throughput. Required for WiFi 5 speeds up to 866 Mbps on 80 MHz.',
                         nl: 'Schakel 802.11ac Very High Throughput in of uit. Vereist voor WiFi 5 snelheden tot 866 Mbps op 80 MHz.' } },
            rtw_he_enable:     {
                label: { en: '802.11ax (HE)', nl: '802.11ax (HE)' },
                desc:  { en: 'Enable or disable 802.11ax High Efficiency. This is WiFi 6 \u2014 the newest standard with higher speeds and better behaviour in crowded environments.',
                         nl: 'Schakel 802.11ax High Efficiency in of uit. Dit is WiFi 6 \u2014 de nieuwste standaard met hogere snelheden en betere prestaties in drukke omgevingen.' } },
            rtw_wireless_mode: {
                label: { en: 'Wireless mode (bitmask)', nl: 'Draadloze Modus (bitmask)' },
                desc:  { en: 'Bitmask of supported wireless modes. 0 = automatic (all modes). Change only if you want to force specific modes.',
                         nl: 'Bitmask voor ondersteunde draadloze modi. 0 = automatisch (alle modi). Wijzig alleen als u specifieke modi wilt forceren.' } },
            rtw_band_type:     {
                label: { en: 'Frequency band', nl: 'Frequentieband' },
                desc:  { en: 'Pick which frequency bands the adapter may use. Dual-band (default) gives the best compatibility.',
                         nl: 'Kies welke frequentiebanden de adapter mag gebruiken. Dual-band (standaard) biedt de beste compatibiliteit.' } },
        }
    },
    channel: {
        labelKey: 'adv.cat.channel',
        params: {
            rtw_channel:       {
                label: { en: 'Default channel', nl: 'Standaard Kanaal' },
                desc:  { en: 'Default channel at startup. 0 = automatic. For 2.4 GHz: 1\u201313. For 5 GHz: 36, 40, 44, 48, 52, \u2026',
                         nl: 'Het standaardkanaal bij opstarten. 0 = automatisch. Voor 2.4 GHz: 1\u201313. Voor 5 GHz: 36, 40, 44, 48, 52, etc.' } },
            rtw_bw_mode:       {
                label: { en: 'Channel width (bitmask)', nl: 'Kanaal Breedte (bitmask)' },
                desc:  { en: 'Bitmask of channel width per band. Bits 0\u20133: 2.4 GHz (0x01=20MHz, 0x03=40MHz). Bits 4\u20137: 5 GHz (0x10=20MHz, 0x30=40MHz, 0x70=80MHz). Default 0x31 (40 MHz 2.4G + 80 MHz 5G).',
                         nl: 'Bitmask voor kanaalbreedte per band. Bits 0\u20133: 2.4 GHz (0x01=20MHz, 0x03=40MHz). Bits 4\u20137: 5 GHz (0x10=20MHz, 0x30=40MHz, 0x70=80MHz). Standaard 0x31 (40 MHz 2.4G + 80 MHz 5G).' } },
            rtw_channel_plan:  {
                label: { en: 'Channel plan', nl: 'Kanaalplan' },
                desc:  { en: 'Regulatory channel plan (0x00\u20130xFF). Decides which channels are available per region. 0xFF = automatic.',
                         nl: 'Reguleringskanaalplan (0x00\u20130xFF). Bepaalt welke kanalen beschikbaar zijn op basis van regio. 0xFF = automatisch.' } },
            rtw_country_code:  {
                label: { en: 'Country code', nl: 'Landcode' },
                desc:  { en: 'ISO 3166-1 alpha-2 country code (e.g. NL, US, DE, GB). Decides regulatory domain and available channels / TX power.',
                         nl: 'ISO 3166-1 alpha-2 landcode (bijv. NL, US, DE, GB). Bepaalt reguleringsdomein en beschikbare kanalen/vermogen.' } },
        }
    },
    power: {
        labelKey: 'adv.cat.power',
        params: {
            rtw_power_mgnt:    {
                label: { en: 'Power management mode', nl: 'Power Management Modus' },
                desc:  { en: 'Power management level. Off = maximum performance but higher consumption. Maximum = longest battery life but possibly lower throughput.',
                         nl: 'Stel het energiebeheerniveau in. Uit = maximale prestaties maar hoger verbruik. Maximaal = langste batterijduur maar mogelijk lagere throughput.' } },
            rtw_ips_mode:      {
                label: { en: 'Idle Power Save (IPS)', nl: 'Idle Power Save (IPS)' },
                desc:  { en: 'Power saving when the adapter is idle. Normal turns the radio off when idle. Level 2 is more aggressive.',
                         nl: 'Energiebesparing wanneer de adapter inactief is. Normaal schakelt de radio uit bij inactiviteit. Level 2 is agressiever.' } },
            rtw_lps_level:     {
                label: { en: 'Low Power Save level', nl: 'Low Power Save Niveau' },
                desc:  { en: 'Power saving level while connected. Clock Gating saves moderately. Power Gating saves the most but can increase latency.',
                         nl: 'Energiebesparingsniveau tijdens verbinding. Clock Gating bespaart matig. Power Gating bespaart maximaal maar kan latentie verhogen.' } },
        }
    },
    performance: {
        labelKey: 'adv.cat.performance',
        params: {
            rtw_ampdu_enable:  {
                label: { en: 'AMPDU', nl: 'AMPDU' },
                desc:  { en: 'Aggregate MAC Protocol Data Unit. Bundles multiple frames into one transmission for higher throughput. Recommended: On.',
                         nl: 'Aggregate MAC Protocol Data Unit. Bundelt meerdere frames in \u00e9\u00e9n transmissie voor hogere throughput. Aanbevolen: Aan.' } },
            rtw_en_napi:       {
                label: { en: 'NAPI', nl: 'NAPI' },
                desc:  { en: 'New API for network-interrupt handling. Reduces CPU load at high packet rates. Recommended: On.',
                         nl: 'New API voor netwerkinterruptverwerking. Vermindert CPU-belasting bij hoge pakketsnelheden. Aanbevolen: Aan.' } },
            rtw_en_gro:        {
                label: { en: 'GRO', nl: 'GRO' },
                desc:  { en: 'Generic Receive Offload. Coalesces small received packets into larger ones for more efficient processing. Recommended: On.',
                         nl: 'Generic Receive Offload. Combineert kleine ontvangen pakketten tot grotere voor effici\u00ebntere verwerking. Aanbevolen: Aan.' } },
            rtw_switch_usb_mode: {
                label: { en: 'USB mode', nl: 'USB Modus' },
                desc:  { en: 'Force USB 2.0 or 3.0 mode. USB 3.0 gives higher speeds but can cause interference on 2.4 GHz. No change = automatic.',
                         nl: 'Forceer USB 2.0 of 3.0 modus. USB 3.0 biedt hogere snelheden maar kan interferentie op 2.4 GHz veroorzaken. Geen wijziging = automatisch.' } },
            rtw_wmm_enable:    {
                label: { en: 'WMM / QoS', nl: 'WMM / QoS' },
                desc:  { en: 'WiFi Multimedia / Quality of Service. Prioritises voice and video traffic over bulk data. Recommended: On.',
                         nl: 'WiFi Multimedia / Quality of Service. Prioriteert spraak- en videoverkeer boven bulkdata. Aanbevolen: Aan.' } },
        }
    },
    antenna: {
        labelKey: 'adv.cat.antenna',
        params: {
            rtw_beamform_cap:  {
                label: { en: 'Beamforming capability', nl: 'Beamforming Capaciteit' },
                desc:  { en: 'Beamforming bitmask. 0 = Off. Common values: 0x82 = SU Beamformee, 0x8A = SU+MU Beamformee. Beamforming aims the signal at the device for better range.',
                         nl: 'Beamforming bitmask. 0 = Uit. Veelgebruikte waarden: 0x82 = SU Beamformee, 0x8A = SU+MU Beamformee. Beamforming richt het signaal naar het apparaat voor beter bereik.' } },
            rtw_dyn_txbf:      {
                label: { en: 'Dynamic TX Beamforming', nl: 'Dynamische TX Beamforming' },
                desc:  { en: 'Dynamically switch between beamforming modes based on channel conditions. Recommended: On when beamforming is active.',
                         nl: 'Dynamisch schakelen tussen beamforming-modi op basis van kanaalcondities. Aanbevolen: Aan als beamforming actief is.' } },
            rtw_tx_nss:        {
                label: { en: 'TX Spatial Streams', nl: 'TX Spatial Streams' },
                desc:  { en: 'Number of transmit spatial streams. Auto lets the driver choose. 2 streams = maximum speed. 1 stream = lower power.',
                         nl: 'Aantal zend-spatial streams. Auto laat de driver kiezen. 2 streams = maximale snelheid. 1 stream = lager verbruik.' } },
            rtw_rx_nss:        {
                label: { en: 'RX Spatial Streams', nl: 'RX Spatial Streams' },
                desc:  { en: 'Number of receive spatial streams. Auto lets the driver choose. 2 streams = maximum speed.',
                         nl: 'Aantal ontvangst-spatial streams. Auto laat de driver kiezen. 2 streams = maximale snelheid.' } },
            rtw_antdiv_cfg:    {
                label: { en: 'Antenna diversity', nl: 'Antenne Diversiteit' },
                desc:  { en: 'Antenna diversity configuration. On = driver picks the best antenna. Auto (Efuse) = use factory settings.',
                         nl: 'Antenne-diversiteitconfiguratie. Aan = driver kiest beste antenne. Auto (Efuse) = gebruik fabrieksinstellingen.' } },
            rtw_rx_stbc:       {
                label: { en: 'RX STBC', nl: 'RX STBC' },
                desc:  { en: 'Space-Time Block Coding on receive. Improves reliability and range by adding redundancy across antennas. Both bands recommended.',
                         nl: 'Space-Time Block Coding voor ontvangst. Verbetert betrouwbaarheid en bereik door redundantie over antennes. Beide banden aanbevolen.' } },
        }
    },
    roaming: {
        labelKey: 'adv.cat.roaming',
        params: {
            rtw_max_roaming_times: {
                label: { en: 'Max roaming attempts', nl: 'Max Roaming Pogingen' },
                desc:  { en: 'Maximum number of times the adapter tries to roam to a better access point. 0 = roaming disabled. Higher values = more aggressive roaming.',
                         nl: 'Maximum aantal keren dat de adapter probeert te roamen naar een beter access point. 0 = roaming uitgeschakeld. Hogere waarden = agressiever roaming.' } },
            rtw_btcoex_enable: {
                label: { en: 'Bluetooth coexistence', nl: 'Bluetooth Coexistentie' },
                desc:  { en: 'Enable WiFi/Bluetooth coexistence. Prevents interference when Bluetooth is active. Auto = use factory settings.',
                         nl: 'Schakel WiFi/Bluetooth coexistentie in. Voorkomt interferentie wanneer Bluetooth tegelijk actief is. Auto = gebruik fabrieksinstellingen.' } },
        }
    },
    debug: {
        labelKey: 'adv.cat.debug',
        params: {
            rtw_drv_log_level: {
                label: { en: 'Log level', nl: 'Log Niveau' },
                desc:  { en: 'Driver log level in dmesg / kernel log. None = critical errors only. Debug = full diagnostics (slows the driver).',
                         nl: 'Driver log-niveau in dmesg/kernel log. Geen = alleen kritieke fouten. Debug = volledige diagnostiek (vertraagt de driver).' } },
            rtw_tx_pwr_by_rate: {
                label: { en: 'TX Power by Rate', nl: 'TX Power by Rate' },
                desc:  { en: 'Adjust TX power per data rate. On = follow the power-by-rate table. Auto = use factory settings from efuse.',
                         nl: 'Pas zendvermogen aan per datasnelheid. Aan = volg de power-by-rate tabel. Auto = gebruik fabrieksinstellingen uit efuse.' } },
            rtw_tx_pwr_lmt_enable: {
                label: { en: 'TX Power Limit', nl: 'TX Power Limiet' },
                desc:  { en: 'Cap TX power according to regulatory limits. Recommended: On or Auto to comply with local law.',
                         nl: 'Beperk zendvermogen volgens reguleringslimieten. Aanbevolen: Aan of Auto om te voldoen aan lokale wetgeving.' } },
        }
    }
};

async function loadAdvanced() {
    try {
        const r = await fetch('/api/advanced');
        const d = await r.json();
        advData = d.parameters || {};
        advChanges = {};
        advLoaded = true;
        renderAdvCategories();
        if (!advSelectedCat) {
            advSelectedCat = 'wireless';
            renderAdvCategories();
            renderAdvProperties('wireless');
        }
        updatePendingBanner(d.has_pending_changes);
    } catch(e) {
        console.error('Failed to load advanced settings:', e);
    }
}

function renderAdvCategories() {
    const el = document.getElementById('adv-categories');
    let html = '';
    for (const [key, cat] of Object.entries(ADV_SETTINGS)) {
        html += '<div class="adv-cat' + (advSelectedCat === key ? ' active' : '') +
                '" onclick="selectAdvCategory(\''+key+'\')">'+t(cat.labelKey)+'</div>';
    }
    el.innerHTML = html;
}

function selectAdvCategory(key) {
    advSelectedCat = key;
    advSelectedParam = null;
    renderAdvCategories();
    renderAdvProperties(key);
    document.getElementById('adv-editor').innerHTML = `<div class="adv-empty">${t('adv.pickprop')}</div>`;
}

function renderAdvProperties(catKey) {
    const el = document.getElementById('adv-proplist');
    const cat = ADV_SETTINGS[catKey];
    if (!cat) { el.innerHTML = ''; return; }
    let html = '';
    for (const [pname, pdef] of Object.entries(cat.params)) {
        const modified = pname in advChanges;
        html += '<div class="adv-prop' + (advSelectedParam === pname ? ' active' : '') +
                '" onclick="selectAdvParam(\''+catKey+'\',\''+pname+'\')">' +
                '<span>'+L(pdef)+'</span>' +
                (modified ? '<span class="adv-modified-dot"></span>' : '') +
                '</div>';
    }
    el.innerHTML = html;
}

function selectAdvParam(catKey, pname) {
    advSelectedParam = pname;
    renderAdvProperties(catKey);
    renderAdvEditor(catKey, pname);
}

function renderAdvEditor(catKey, pname) {
    const el = document.getElementById('adv-editor');
    const pdef = ADV_SETTINGS[catKey].params[pname];
    const paramData = advData[pname] || {};
    const currentVal = pname in advChanges ? advChanges[pname] : paramData.current;
    const isAvailable = paramData.current !== null && paramData.current !== undefined;

    if (!isAvailable) {
        el.innerHTML = '<div class="adv-editor-label">'+t('label.property')+'</div>' +
            '<div class="adv-editor-name">'+L(pdef)+'</div>' +
            '<div style="color:#fca5a5;padding:12px;background:#7f1d1d;border-radius:8px;">'+t('adv.unavailable')+'</div>' +
            '<div class="adv-desc" style="margin-top:auto;">'+D(pdef)+'</div>';
        return;
    }

    let inputHtml = '';
    const serverOpts = getParamOptions(pname);
    if (serverOpts) {
        inputHtml = '<select onchange="advValueChanged(\''+pname+'\', this.value)">';
        for (const [val, optKey] of Object.entries(serverOpts)) {
            inputHtml += '<option value="'+val+'"'+(String(currentVal)===val?' selected':'')+'>'+t(optKey)+' ('+val+')</option>';
        }
        inputHtml += '</select>';
    } else {
        inputHtml = '<input type="text" value="'+esc(currentVal)+'" onchange="advValueChanged(\''+pname+'\', this.value)">';
    }

    const pendingVal = paramData.pending;
    const statusHtml = '<span class="badge-module">'+t('adv.modulerestart')+'</span>';
    let pendingHtml = '';
    if (pendingVal !== undefined && pendingVal !== null && String(pendingVal) !== String(paramData.current)) {
        pendingHtml = '<div class="adv-current" style="color:#fbbf24;">'+t('label.pending')+': '+esc(pendingVal)+'</div>';
    }

    el.innerHTML =
        '<div class="adv-editor-label">'+t('label.property')+'</div>' +
        '<div class="adv-editor-name">'+L(pdef)+' '+statusHtml+'</div>' +
        '<div class="adv-editor-input">'+inputHtml+'</div>' +
        '<div class="adv-current">'+t('label.current')+': '+esc(paramData.current)+'</div>' +
        pendingHtml +
        '<div class="adv-desc">'+D(pdef)+'</div>';
}

function getParamOptions(pname) {
    // Each option value maps to an i18n key resolved at render time.
    const opts = {
        rtw_ht_enable:     {'0':'opt.off','1':'opt.on'},
        rtw_vht_enable:    {'0':'opt.off','1':'opt.on','2':'opt.auto'},
        rtw_he_enable:     {'0':'opt.off','1':'opt.on','2':'opt.auto'},
        rtw_band_type:     {'1':'opt.only24','2':'opt.only5','3':'opt.dualband'},
        rtw_power_mgnt:    {'0':'opt.off','1':'opt.minimal','2':'opt.maximal'},
        rtw_ips_mode:      {'0':'opt.none','1':'opt.normal','2':'opt.level2'},
        rtw_lps_level:     {'0':'opt.normal','1':'opt.clockgating','2':'opt.powergating'},
        rtw_ampdu_enable:  {'0':'opt.off','1':'opt.on'},
        rtw_en_napi:       {'0':'opt.off','1':'opt.on'},
        rtw_en_gro:        {'0':'opt.off','1':'opt.on'},
        rtw_switch_usb_mode: {'0':'opt.nochange','1':'opt.usb3','2':'opt.usb2'},
        rtw_wmm_enable:    {'0':'opt.off','1':'opt.on'},
        rtw_dyn_txbf:      {'0':'opt.off','1':'opt.on'},
        rtw_tx_nss:        {'0':'opt.auto','1':'opt.1stream','2':'opt.2streams'},
        rtw_rx_nss:        {'0':'opt.auto','1':'opt.1stream','2':'opt.2streams'},
        rtw_antdiv_cfg:    {'0':'opt.off','1':'opt.on','2':'opt.auto_efuse'},
        rtw_rx_stbc:       {'0':'opt.off','1':'opt.only24','2':'opt.only5','3':'opt.both_bands'},
        rtw_btcoex_enable: {'0':'opt.off','1':'opt.on','2':'opt.auto_efuse'},
        rtw_drv_log_level: {'0':'opt.none','1':'opt.error','2':'opt.warning','3':'opt.notice','4':'opt.info','5':'opt.debug'},
        rtw_tx_pwr_by_rate: {'0':'opt.off','1':'opt.on','2':'opt.auto_efuse'},
        rtw_tx_pwr_lmt_enable: {'0':'opt.off','1':'opt.on','2':'opt.auto_efuse'},
    };
    return opts[pname] || null;
}

function advValueChanged(pname, value) {
    const paramData = advData[pname] || {};
    if (String(value) === String(paramData.current)) {
        delete advChanges[pname];
    } else {
        advChanges[pname] = value;
    }
    if (advSelectedCat) renderAdvProperties(advSelectedCat);
    updatePendingBanner(Object.keys(advChanges).length > 0);
}

async function saveAdvanced() {
    if (Object.keys(advChanges).length === 0) {
        showToast(t('toast.nochanges'), false);
        return;
    }
    const moduleParams = {};
    for (const [k, v] of Object.entries(advChanges)) {
        moduleParams[k] = v;
    }
    try {
        const r = await fetch('/api/advanced', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({module: moduleParams})
        });
        const d = await r.json();
        showToast(d.reload_needed ? t('toast.savedrestart') : t('toast.saved'), true);
        advChanges = {};
        await loadAdvanced();
        if (advSelectedCat && advSelectedParam) {
            renderAdvProperties(advSelectedCat);
            renderAdvEditor(advSelectedCat, advSelectedParam);
        }
    } catch(e) {
        showToast(t('toast.saveerr'), false);
    }
}

function resetAdvanced() {
    advChanges = {};
    if (advSelectedCat) renderAdvProperties(advSelectedCat);
    if (advSelectedCat && advSelectedParam) renderAdvEditor(advSelectedCat, advSelectedParam);
    updatePendingBanner(false);
    showToast(t('toast.resetlocal'), true);
}

async function reloadModule() {
    if (!confirm(t('adv.reloadconfirm'))) return;
    showToast(t('toast.reloading'), true);
    try {
        const r = await fetch('/api/advanced/reload', {method: 'POST'});
        const d = await r.json();
        if (d.success) {
            showToast(d.message || t('toast.reloaded'), true);
            advLoaded = false;
            setTimeout(() => { loadAdvanced(); refreshStatus(); }, 2000);
        } else {
            showToast(d.error || t('toast.reloadfail'), false);
        }
    } catch(e) {
        showToast(t('toast.reloaderr'), false);
    }
}

function updatePendingBanner(show) {
    const el = document.getElementById('adv-pending-banner');
    if (show) {
        const n = Object.keys(advChanges).length;
        let txt;
        if (n > 0) {
            txt = n + (n === 1 ? t('adv.pending_1') : t('adv.pending_n'));
        } else {
            txt = t('adv.pending_saved');
        }
        el.textContent = '\u26A0 ' + txt;
        el.style.display = 'block';
    } else {
        el.style.display = 'none';
    }
}

// ── Live updates via Server-Sent Events ─────────────────────────────
const AUTH_TOKEN = document.querySelector('meta[name="rtw-token"]').content;
let STREAM = null;
let LAST_STATUS = null;

function applyStatusPayload(d) {
    LAST_STATUS = d;
    const badge = document.getElementById('status-badge');
    if (!d.driver_loaded) {
        badge.textContent = t('status.driver_off');
        badge.className = 'status-badge badge-err';
        return;
    }
    badge.textContent = d.operstate === 'up' || d.operstate === 'dormant'
        ? t('status.connected') : t('status.disconnected');
    badge.className = 'status-badge ' + (d.connection.ssid ? 'badge-ok' : 'badge-err');

    document.getElementById('adapter-info').innerHTML = `
        <div class="info-row"><span class="info-label">${t('label.interface')}</span><span class="info-value">${esc(d.interface)}</span></div>
        <div class="info-row"><span class="info-label">${t('label.mac')}</span><span class="info-value">${esc(d.mac_address)}</span></div>
        <div class="info-row"><span class="info-label">${t('label.ip')}</span><span class="info-value">${d.ip_address ? esc(d.ip_address) : t('status.none')}</span></div>
        <div class="info-row"><span class="info-label">${t('label.status')}</span><span class="info-value">${esc(d.operstate)}</span></div>
        <div class="info-row"><span class="info-label">${t('label.mtu')}</span><span class="info-value">${esc(d.mtu)}</span></div>
        <div class="info-row"><span class="info-label">${t('label.usbspeed')}</span><span class="info-value">${esc(d.usb_speed_mbps)} Mbps</span></div>
        <div class="info-row"><span class="info-label">${t('label.usbdev')}</span><span class="info-value">${esc(d.usb_vendor)}:${esc(d.usb_product)} (${esc(d.usb_product_name)})</span></div>
    `;

    const conn = d.connection;
    let connHtml = '';
    if (conn.ssid) {
        const pct = signalPercent(conn.signal_dbm);
        const col = signalColor(conn.signal_dbm);
        connHtml = `
            <div class="info-row"><span class="info-label">${t('th.ssid')}</span><span class="info-value">${esc(conn.ssid)}</span></div>
            <div class="info-row"><span class="info-label">${t('label.signal')}</span><span class="info-value">${esc(conn.signal_dbm)} dBm</span></div>
            <div class="signal-bar"><div class="signal-fill" style="width:${pct}%;background:${col};"></div></div>
            <div class="info-row"><span class="info-label">${t('label.freq')}</span><span class="info-value">${esc(conn.frequency_mhz)} MHz</span></div>
            <div class="info-row"><span class="info-label">${t('label.txbitrate')}</span><span class="info-value">${esc(conn.tx_bitrate || 'N/A')}</span></div>
        `;
    } else {
        connHtml = `<div style="color:var(--text-dim);padding:20px;text-align:center;">${t('conn.notconnected')}</div>`;
    }
    document.getElementById('connection-info').innerHTML = connHtml;

    const s = d.statistics;
    document.getElementById('stats-info').innerHTML = `
        <div class="stat-box"><div class="stat-value">${formatBytes(s.tx_bytes)}</div><div class="stat-label">${t('stat.tx_data')}</div></div>
        <div class="stat-box"><div class="stat-value">${formatBytes(s.rx_bytes)}</div><div class="stat-label">${t('stat.rx_data')}</div></div>
        <div class="stat-box"><div class="stat-value">${s.tx_packets.toLocaleString()}</div><div class="stat-label">${t('stat.tx_pkts')}</div></div>
        <div class="stat-box"><div class="stat-value">${s.rx_packets.toLocaleString()}</div><div class="stat-label">${t('stat.rx_pkts')}</div></div>
        <div class="stat-box"><div class="stat-value">${esc(s.tx_errors)}</div><div class="stat-label">${t('stat.tx_err')}</div></div>
        <div class="stat-box"><div class="stat-value">${esc(s.rx_errors)}</div><div class="stat-label">${t('stat.rx_err')}</div></div>
        <div class="stat-box"><div class="stat-value">${esc(s.tx_dropped)}</div><div class="stat-label">${t('stat.tx_drop')}</div></div>
        <div class="stat-box"><div class="stat-value">${esc(s.rx_dropped)}</div><div class="stat-label">${t('stat.rx_drop')}</div></div>
    `;
}

function startStream() {
    if (STREAM) STREAM.close();
    STREAM = new EventSource('/api/stream?token=' + encodeURIComponent(AUTH_TOKEN));
    STREAM.addEventListener('status', e => {
        try { applyStatusPayload(JSON.parse(e.data)); }
        catch (err) { console.warn('SSE parse failed', err); }
    });
    STREAM.onerror = () => { /* EventSource auto-reconnects */ };
}

// Override refreshStatus so the in-place buttons (e.g. after connect/
// disconnect) still produce an immediate refresh — the stream will
// follow up within ~2 s.
async function refreshStatus() {
    try {
        const r = await fetch('/api/status');
        applyStatusPayload(await r.json());
    } catch (e) { /* stream will catch up */ }
}

// ── Initial load and auto-refresh ───────────────────────────────────
document.documentElement.setAttribute('data-theme', THEME);
applyTranslations();
startStream();
refreshDriverInfo();
refreshTrends();
setInterval(() => { if (!_LONG_RUN_PAUSED) refreshTrends(); }, 5000);
setInterval(() => {
    if (_LONG_RUN_PAUSED) return;
    // Spectrum re-fetch only when the Networks tab is the active one.
    if (document.getElementById('tab-networks').classList.contains('active')) {
        refreshSpectrum();
    }
}, 30000);
setInterval(() => {
    if (_LONG_RUN_PAUSED) return;
    // While the Monitor tab is open, keep status + frame buffer fresh.
    const monTab = document.getElementById('tab-monitor');
    if (monTab && monTab.classList.contains('active')) {
        refreshMonitorStatus();
        if (MONITOR_INFO && MONITOR_INFO.capturing) refreshFrames();
    }
}, 2000);
