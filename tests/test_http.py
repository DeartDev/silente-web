"""Checks on the running container (spec §6.1, §7.2, §9: LP-03, LP-12).

Skipped unless SILENTE_URL points at a running server:

    docker compose up -d --build
    SILENTE_URL=http://localhost:9020 python3 -m unittest tests.test_http -v
"""

import os
import re
import unittest
import urllib.error
import urllib.request

BASE = os.environ.get("SILENTE_URL", "").rstrip("/")
CSP = (
    "default-src 'none'; img-src 'self'; style-src 'self'; font-src 'self'; connect-src 'self'; "
    "base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def fetch(path: str, method: str = "GET"):
    """Status, headers and body, without following redirects."""
    request = urllib.request.Request(BASE + path, method=method, data=b"x" if method == "POST" else None)
    try:
        with OPENER.open(request, timeout=10) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.headers, error.read()


@unittest.skipUnless(BASE, "SILENTE_URL no está definida")
class HttpTest(unittest.TestCase):
    def test_pages_answer_200_with_utf8_html(self):
        for path in ("/", "/privacidad", "/terminos"):
            with self.subTest(path=path):
                status, headers, body = fetch(path)
                self.assertEqual(status, 200)
                self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
                self.assertEqual(headers["Cache-Control"], "no-cache")
                self.assertIn(b"<title>", body)

    def test_security_headers_on_every_response(self):
        assets = re.findall(rb'href="(/assets/site\.[^"]+)"', fetch("/")[2])
        for path in ("/", "/privacidad", "/no-existe", "/salud", assets[0].decode()):
            with self.subTest(path=path):
                _, headers, _ = fetch(path)
                self.assertEqual(headers["Content-Security-Policy"], CSP)
                self.assertEqual(headers["Cross-Origin-Opener-Policy"], "same-origin")
                self.assertEqual(headers["Cross-Origin-Resource-Policy"], "same-origin")

    # LP-03
    def test_no_cookies_and_no_server_version(self):
        for path in ("/", "/privacidad", "/no-existe"):
            with self.subTest(path=path):
                _, headers, _ = fetch(path)
                self.assertIsNone(headers["Set-Cookie"])
                self.assertNotRegex(headers.get("Server", ""), r"\d")
                self.assertIsNone(headers["Allow"])

    # LP-12
    def test_unknown_paths_answer_404_with_the_silente_page(self):
        for path in ("/no-existe", "/404", "/404.html", "/licencias", "/assets/no-existe.css"):
            with self.subTest(path=path):
                status, headers, body = fetch(path)
                self.assertEqual(status, 404)
                self.assertIn("Esta página no existe", body.decode("utf-8"))

    def test_html_and_trailing_slash_redirect_to_the_canonical_url(self):
        cases = {
            "/privacidad.html": "/privacidad",
            "/privacidad/": "/privacidad",
            "/terminos.html": "/terminos",
            "/index.html": "/",
            "/privacidad.html?a=1": "/privacidad?a=1",
        }
        for path, target in cases.items():
            with self.subTest(path=path):
                status, headers, _ = fetch(path)
                self.assertEqual(status, 301)
                self.assertEqual(headers["Location"], target)

    def test_only_get_and_head(self):
        self.assertEqual(fetch("/", "HEAD")[0], 200)
        for method in ("POST", "PUT", "DELETE", "OPTIONS"):
            with self.subTest(method=method):
                status, headers, _ = fetch("/", method)
                self.assertEqual(status, 405)
                self.assertEqual(headers["Allow"], "GET, HEAD")

    def test_assets_are_immutable(self):
        body = fetch("/")[2].decode()
        for path in set(re.findall(r'"(/assets/[^"\s]+)"', body)):
            with self.subTest(path=path):
                status, headers, _ = fetch(path)
                self.assertEqual(status, 200)
                self.assertEqual(headers["Cache-Control"], "public, max-age=31536000, immutable")

    def test_content_types(self):
        body = fetch("/")[2].decode()
        expected = {
            ".css": "text/css; charset=utf-8",
            ".woff2": "font/woff2",
            ".webp": "image/webp",
            ".svg": "image/svg+xml; charset=utf-8",
            ".png": "image/png",
        }
        for path in set(re.findall(r'"(/assets/[^"\s]+)"', body)):
            suffix = path[path.rindex(".") :]
            with self.subTest(path=path):
                self.assertEqual(fetch(path)[1]["Content-Type"], expected[suffix])
        for path, kind in {"/robots.txt": "text/plain", "/sitemap.xml": "text/xml", "/salud": "text/plain"}.items():
            with self.subTest(path=path):
                status, headers, _ = fetch(path)
                self.assertEqual(status, 200)
                self.assertTrue(headers["Content-Type"].startswith(kind))

    def test_health(self):
        status, headers, body = fetch("/salud")
        self.assertEqual((status, body), (200, b"ok\n"))
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_hidden_files_and_listings_are_denied(self):
        for path in ("/.env", "/.git/config", "/assets/"):
            with self.subTest(path=path):
                self.assertIn(fetch(path)[0], (301, 403, 404))
        self.assertEqual(fetch("/.env")[0], 403)


if __name__ == "__main__":
    unittest.main()
