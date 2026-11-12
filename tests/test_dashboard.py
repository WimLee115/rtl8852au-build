#!/usr/bin/env python3
"""
Offline security regression tests for the dashboard (dashboard/app.py).

No hardware, no root: Flask's test client drives the app in-process, the
auth token lives in a temporary XDG_CONFIG_HOME, and the modprobe config the
Advanced tab writes is redirected to a temporary file.

    python3 -m unittest tests.test_dashboard -v

SPDX-License-Identifier: GPL-2.0
"""

import base64
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

_APP_PATH = Path(__file__).resolve().parent.parent / "dashboard" / "app.py"


def _load_app(config_home):
    """Import dashboard/app.py with its token stored under config_home."""
    old = os.environ.get("XDG_CONFIG_HOME")
    os.environ["XDG_CONFIG_HOME"] = config_home
    try:
        spec = importlib.util.spec_from_file_location("rtw_dashboard_under_test", _APP_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        if old is None:
            os.environ.pop("XDG_CONFIG_HOME", None)
        else:
            os.environ["XDG_CONFIG_HOME"] = old
    return module


class DashboardTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dash = _load_app(cls._tmp.name)
        cls.dash.ALLOWED_HOSTS.update({"localhost"})
        cls.client = cls.dash.app.test_client()
        creds = base64.b64encode(f"user:{cls.dash.AUTH_TOKEN}".encode()).decode()
        cls.auth = {"Authorization": f"Basic {creds}"}

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def setUp(self):
        self.conf = Path(self._tmp.name) / "8852au.conf"
        if self.conf.exists():
            self.conf.unlink()
        self.dash.MODPROBE_CONF = str(self.conf)

    def save_module_params(self, params, **headers):
        return self.client.post("/api/advanced", json={"module": params},
                                headers={**self.auth, **headers})


class TestModprobeInjection(DashboardTestCase):
    """The Advanced tab writes /etc/modprobe.d/8852au.conf, which modprobe
    parses as root. A value carrying a newline used to start a directive of
    its own -- `install 8852au <cmd>` runs <cmd> on the next module load."""

    def test_01_country_code_with_newline_is_rejected(self):
        r = self.save_module_params({"rtw_country_code": "NL\ninstall 8852au /bin/sh -c id"})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(self.conf.exists())
        self.assertEqual(r.get_json()["results"], [])

    def test_02_country_code_with_space_is_rejected(self):
        self.save_module_params({"rtw_country_code": "NL rtw_ht_enable=0"})
        self.assertFalse(self.conf.exists())

    def test_03_valid_country_code_is_saved(self):
        self.save_module_params({"rtw_country_code": "NL"})
        self.assertIn("options 8852au rtw_country_code=NL\n", self.conf.read_text())

    def test_04_number_is_written_in_canonical_form(self):
        # int() accepts " 36\n"; the raw string must not reach the file.
        self.save_module_params({"rtw_channel": " 36\n"})
        options = [ln for ln in self.conf.read_text().splitlines() if ln.startswith("options")]
        self.assertEqual(options, ["options 8852au rtw_channel=36"])

    def test_05_unsafe_value_already_in_file_is_not_rewritten(self):
        self.conf.write_text("options 8852au rtw_country_code=N;L\n")
        self.save_module_params({"rtw_ht_enable": "1"})
        text = self.conf.read_text()
        self.assertIn("rtw_ht_enable=1", text)
        self.assertNotIn("N;L", text)


class TestCrossSiteRequests(DashboardTestCase):
    """Basic Auth is ambient: a form on another site can make the browser
    POST here with the cached credentials attached."""

    def test_01_foreign_origin_is_refused(self):
        r = self.save_module_params({}, Origin="http://evil.example")
        self.assertEqual(r.status_code, 403)

    def test_02_cross_site_fetch_metadata_is_refused(self):
        r = self.save_module_params({}, **{"Sec-Fetch-Site": "cross-site"})
        self.assertEqual(r.status_code, 403)

    def test_03_same_site_other_port_is_refused(self):
        r = self.save_module_params({}, **{"Sec-Fetch-Site": "same-site"})
        self.assertEqual(r.status_code, 403)

    def test_04_same_origin_is_allowed(self):
        r = self.save_module_params({}, Origin="http://localhost",
                                    **{"Sec-Fetch-Site": "same-origin"})
        self.assertEqual(r.status_code, 200)

    def test_05_client_without_browser_headers_is_allowed(self):
        self.assertEqual(self.save_module_params({}).status_code, 200)

    def test_06_get_is_not_affected(self):
        r = self.client.get("/api/advanced", headers={**self.auth, "Sec-Fetch-Site": "cross-site"})
        self.assertEqual(r.status_code, 200)


class TestSecurityHeaders(DashboardTestCase):
    def test_01_headers_present(self):
        r = self.client.get("/api/advanced", headers=self.auth)
        self.assertEqual(r.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(r.headers.get("X-Frame-Options"), "DENY")
        self.assertIn("frame-ancestors 'none'", r.headers.get("Content-Security-Policy", ""))
        self.assertIn("base-uri 'none'", r.headers.get("Content-Security-Policy", ""))

    def test_02_headers_present_on_auth_failure(self):
        r = self.client.get("/api/advanced")
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.headers.get("X-Frame-Options"), "DENY")


if __name__ == "__main__":
    unittest.main(verbosity=2)
