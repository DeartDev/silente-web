"""Checks on the generated site (spec §9: LP-01…LP-04, LP-10, LP-12; §6, §7).

    python3 -m unittest discover -s tests -t .
"""

import re
import shutil
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

import build
from tools.check_brand_name import site_hits, versioned_hits

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = build.SITE_URL
PAGES = ["index.html", "privacidad.html", "terminos.html", "404.html"]
LEGAL = {"privacidad.html": "politica-de-privacidad.md", "terminos.html": "terminos-de-uso.md"}
# Navigation to other origins allowed in <a href> (LP-02).
ALLOWED_LINKS = ("mailto:pqrs@nordirwork.com", "https://play.google.com/store/apps/details?id=com.nordirwork.silente")
# Attributes that make the browser fetch something.
RESOURCE_ATTRS = {"src", "srcset", "poster", "data", "action", "formaction"}


class Page(HTMLParser):
    """Collects tags, text and headings of an HTML page."""

    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str]]] = []
        self.text: list[str] = []
        self.headings: list[int] = []
        self.ids: set[str] = set()
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attributes = {name: value or "" for name, value in attrs}
        self.tags.append((tag, attributes))
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))

    handle_startendtag = handle_starttag

    def handle_data(self, data):
        self.text.append(data)

    def find(self, tag: str) -> list[dict[str, str]]:
        return [attrs for name, attrs in self.tags if name == tag]

    def plain_text(self) -> str:
        return normalize("".join(self.text))


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def markdown_blocks(source: str) -> list[str]:
    """Plain text of each paragraph, heading and list item of a legal text."""
    blocks = []
    for line in source.splitlines():
        line = re.sub(r"^(#+|-|\d+\.)\s+", "", line.strip())
        line = re.sub(r"\*\*(.+?)\*\*|\*(.+?)\*", lambda m: m.group(1) or m.group(2), line)
        line = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", line)
        if line:
            blocks.append(normalize(line))
    return blocks


class SiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.dist = cls.tmp / "dist"
        build.build(cls.dist)
        cls.sources = {name: (cls.dist / name).read_text(encoding="utf-8") for name in PAGES}
        cls.pages = {name: Page(source) for name, source in cls.sources.items()}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    # LP-01

    def test_legal_pages_reproduce_the_text_and_date(self):
        for page, source in LEGAL.items():
            markdown_text = (ROOT / "legal" / source).read_text(encoding="utf-8")
            text = self.pages[page].plain_text()
            for block in markdown_blocks(markdown_text):
                with self.subTest(page=page, block=block[:60]):
                    self.assertIn(block, text)
            date = re.search(r"^Última actualización: .+$", markdown_text, re.MULTILINE).group(0)
            self.assertIn(date, text)

    def test_build_fails_with_placeholders_or_without_date(self):
        broken = {
            "marcador": "# Política\n\nÚltima actualización: hoy\n\nEscribe a [CORREO DE CONTACTO].\n",
            "sin fecha": "# Política\n\nTexto.\n",
        }
        for case, text in broken.items():
            with self.subTest(case=case):
                legal = self.tmp / f"legal-{case}"
                shutil.copytree(ROOT / "legal", legal)
                (legal / "politica-de-privacidad.md").write_text(text, encoding="utf-8")
                with self.assertRaises(build.BuildError):
                    build.build(self.tmp / f"out-{case}", legal)

    # LP-02

    def test_no_resource_from_another_origin(self):
        for name, page in self.pages.items():
            for tag, attrs in page.tags:
                urls = []
                for attr, value in attrs.items():
                    if attr in RESOURCE_ATTRS:
                        urls += [part.split()[0] for part in value.split(",") if part.strip()]
                if tag == "link":
                    urls.append(attrs.get("href", ""))
                if tag == "meta" and attrs.get("property") == "og:image":
                    urls.append(attrs["content"])
                for url in filter(None, urls):
                    with self.subTest(page=name, tag=tag, url=url):
                        parts = urlsplit(url)
                        self.assertTrue(not parts.scheme or url.startswith(ORIGIN + "/"))

    def test_links_to_other_origins_are_only_contact_and_play(self):
        for name, page in self.pages.items():
            for attrs in page.find("a"):
                href = attrs.get("href", "")
                if urlsplit(href).scheme:
                    with self.subTest(page=name, href=href):
                        self.assertIn(href, ALLOWED_LINKS)

    def test_css_only_loads_from_the_same_origin(self):
        css = next((self.dist / "assets").glob("site.*.css")).read_text(encoding="utf-8")
        for url in re.findall(r"url\(\s*[\"']?([^\"')]+)", css):
            with self.subTest(url=url):
                self.assertTrue(url.startswith("/assets/"))
        self.assertNotIn("@import", css)

    # LP-03

    def test_no_javascript_cookies_forms_or_inline_styles(self):
        forbidden_tags = {"script", "form", "iframe", "object", "embed", "style", "input"}
        for name, page in self.pages.items():
            for tag, attrs in page.tags:
                with self.subTest(page=name, tag=tag):
                    self.assertNotIn(tag, forbidden_tags)
                    self.assertNotIn("style", attrs)
                    self.assertFalse([a for a in attrs if a.startswith("on")])
                    self.assertFalse(attrs.get("href", "").lower().startswith("javascript:"))
            self.assertNotIn("http-equiv", self.sources[name].lower())

    # LP-04

    def test_texts_follow_the_glossary(self):
        avoid = [
            r"\bimport\w* (un|el|los|tus?|mis?) libros?",
            r"\brespaldos?\b",
            r"\bbackups?\b",
            r"\bentradas?\b",
            r"\bpremium\b",
            r"\bbitácora\b",
            r"\bestanterías?\b",
        ]
        for name, page in self.pages.items():
            text = page.plain_text().lower()
            for pattern in avoid:
                with self.subTest(page=name, pattern=pattern):
                    self.assertIsNone(re.search(pattern, text))

    # LP-10

    def test_old_name_does_not_appear(self):
        self.assertEqual(site_hits(self.dist), [])
        self.assertEqual(versioned_hits(ROOT), [])

    # LP-12

    def test_404_page(self):
        page = self.pages["404.html"]
        self.assertIn("Esta página no existe", page.plain_text())
        robots = [m for m in page.find("meta") if m.get("name") == "robots"]
        self.assertEqual(robots[0]["content"], "noindex")
        self.assertFalse([l for l in page.find("link") if l.get("rel") == "canonical"])
        self.assertIn("/assets/site.", self.sources["404.html"])  # same design

    # Spec §6.4: metadata

    def test_metadata_of_each_page(self):
        canonical = {"index.html": "/", "privacidad.html": "/privacidad", "terminos.html": "/terminos"}
        for name, page in self.pages.items():
            with self.subTest(page=name):
                self.assertEqual(page.find("html")[0]["lang"], "es")
                self.assertEqual(len(page.find("title")), 1)
                descriptions = [m for m in page.find("meta") if m.get("name") == "description"]
                self.assertGreater(len(descriptions[0]["content"]), 50)
                links = [l["href"] for l in page.find("link") if l.get("rel") == "canonical"]
                if name in canonical:
                    self.assertEqual(links, [ORIGIN + canonical[name]])

    def test_titles_are_unique(self):
        titles = [re.search(r"<title>(.+?)</title>", s).group(1) for s in self.sources.values()]
        self.assertEqual(len(titles), len(set(titles)))

    def test_robots_sitemap_and_health(self):
        self.assertIn(f"Sitemap: {ORIGIN}/sitemap.xml", (self.dist / "robots.txt").read_text())
        sitemap = (self.dist / "sitemap.xml").read_text()
        locs = re.findall(r"<loc>(.+?)</loc>", sitemap)
        self.assertEqual(locs, [f"{ORIGIN}/", f"{ORIGIN}/privacidad", f"{ORIGIN}/terminos"])
        self.assertEqual((self.dist / "salud").read_text(), "ok\n")

    # Spec §7.3: accessibility basics

    def test_headings_in_order_with_one_h1(self):
        for name, page in self.pages.items():
            with self.subTest(page=name):
                self.assertEqual(page.headings.count(1), 1)
                self.assertEqual(page.headings[0], 1)
                for previous, current in zip(page.headings, page.headings[1:]):
                    self.assertLessEqual(current, previous + 1)

    def test_landmarks_and_skip_link(self):
        for name, page in self.pages.items():
            with self.subTest(page=name):
                for landmark in ("header", "nav", "main", "footer"):
                    self.assertEqual(len(page.find(landmark)), 1, landmark)
                self.assertEqual(page.find("main")[0]["id"], "contenido")
                self.assertEqual(page.find("a")[0]["href"], "#contenido")

    def test_images_have_alt_and_size(self):
        for name, page in self.pages.items():
            for attrs in page.find("img"):
                with self.subTest(page=name, src=attrs["src"]):
                    self.assertGreater(len(attrs.get("alt", "")), 10)
                    self.assertTrue(attrs.get("width") and attrs.get("height"))
        for svg in self.pages["index.html"].find("svg"):
            self.assertEqual(svg.get("aria-hidden"), "true")

    def test_only_the_hero_image_loads_eagerly(self):
        images = self.pages["index.html"].find("img")
        self.assertEqual(images[0].get("fetchpriority"), "high")
        for attrs in images[1:]:
            self.assertEqual(attrs.get("loading"), "lazy")

    def test_play_badge_is_not_a_link_before_publishing(self):
        if build.PLAY_URL is not None:
            self.skipTest("la app ya está publicada")
        badges = [a for a in self.pages["index.html"].find("a") if a.get("class") == "badge"]
        self.assertEqual(len(badges), 1)
        self.assertNotIn("href", badges[0])
        self.assertEqual(badges[0]["aria-disabled"], "true")
        self.assertIn("Próximamente en Google Play", self.pages["index.html"].plain_text())

    # Internal links and assets

    def test_internal_links_and_assets_exist(self):
        routes = {"/": "index.html", "/privacidad": "privacidad.html", "/terminos": "terminos.html"}
        for name, page in self.pages.items():
            for tag, attrs in page.tags:
                for attr in ("href", "src"):
                    url = attrs.get(attr, "")
                    if not url.startswith("/"):
                        continue
                    path, _, fragment = url.partition("#")
                    with self.subTest(page=name, url=url):
                        target = routes.get(path, path.lstrip("/"))
                        self.assertTrue((self.dist / target).is_file())
                        if fragment:
                            self.assertIn(fragment, self.pages[target].ids)

    # Spec §7.1: budgets

    def test_home_page_weight_and_requests(self):
        source = self.sources["index.html"]
        css = next((self.dist / "assets").glob("site.*.css"))
        resources = set(re.findall(r'(?:src|href)="(/assets/[^"]+)"', source))
        resources |= set(re.findall(r"(/assets/[^\s,\"]+) \d+w", source))  # srcset
        resources |= set(re.findall(r'url\("(/assets/[^"]+)"', css.read_text()))
        resources = {r for r in resources if "/og." not in r}  # only for link previews
        total = len(source.encode()) + sum((self.dist / r.lstrip("/")).stat().st_size for r in resources)
        # Everything, as if the browser downloaded both sizes of every image.
        self.assertLessEqual(total, 500 * 1024)
        # Requests: the page plus one size per image and each other resource.
        images = len(self.pages["index.html"].find("img"))
        others = {r for r in resources if not r.endswith(".webp")}
        self.assertLessEqual(1 + images + len(others), 15)


class ContrastTest(unittest.TestCase):
    """WCAG 2.2 AA with the CSS tokens of both themes (spec §7.3)."""

    @staticmethod
    def tokens(block: str) -> dict[str, str]:
        return dict(re.findall(r"--([\w-]+):\s*(#[0-9A-Fa-f]{6})", block))

    @staticmethod
    def ratio(a: str, b: str) -> float:
        def luminance(color: str) -> float:
            channels = [int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
            linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
            return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

        high, low = sorted((luminance(a), luminance(b)), reverse=True)
        return (high + 0.05) / (low + 0.05)

    def test_focus_has_an_inner_ring_in_the_text_colour(self):
        css = (ROOT / "src/css/site.css").read_text(encoding="utf-8")
        rule = re.search(r"\n:focus-visible \{(.+?)\}", css, re.S).group(1)
        self.assertIn("outline: 3px solid var(--accent)", rule)
        self.assertIn("box-shadow: 0 0 0 2px var(--text)", rule)

    def test_text_and_focus_contrast(self):
        css = (ROOT / "src/css/site.css").read_text(encoding="utf-8")
        light_block = re.search(r":root \{(.+?)\}", css, re.S).group(1)
        dark_block = re.search(r"prefers-color-scheme: dark\)\s*\{\s*:root \{(.+?)\}", css, re.S).group(1)
        light = self.tokens(light_block)
        dark = {**light, **self.tokens(dark_block)}
        for theme, t in (("claro", light), ("oscuro", dark)):
            for background in ("bg", "surface"):
                for text in ("text", "text-muted", "gold"):
                    with self.subTest(theme=theme, pair=f"{text} sobre {background}"):
                        self.assertGreaterEqual(self.ratio(t[text], t[background]), 4.5)
                with self.subTest(theme=theme, pair=f"foco sobre {background}"):
                    focus = max(self.ratio(t["accent"], t[background]), self.ratio(t["text"], t[background]))
                    self.assertGreaterEqual(focus, 3)
                with self.subTest(theme=theme, pair=f"bordes sobre {background}"):
                    self.assertGreaterEqual(self.ratio(t["rule"], t[background]), 3)


if __name__ == "__main__":
    unittest.main()
