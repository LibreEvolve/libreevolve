"""Offline site build contracts; no deployment or live-evidence claims."""

from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from _support import temporary_directory

SITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SITE))
import build as builder


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.ids.add(attrs.get("id"))
        for key in ("href", "src"):
            if key in attrs:
                self.urls.append(attrs[key])


class SiteBuildTests(unittest.TestCase):
    def test_tables_have_keyboard_scroll_region_and_column_headers(self):
        rendered = builder.render_markdown("| Name | Value |\n| --- | --- |\n| Cost | Unknown |", "docs/results.md", [], builder.ROOT, "/")
        self.assertIn('role="region"', rendered)
        self.assertIn('tabindex="0"', rendered)
        self.assertIn('aria-label="Scrollable documentation table"', rendered)
        self.assertEqual(rendered.count('scope="col"'), 2)
        self.assertIn('</table></div>', rendered)

    def test_determinism_and_no_execution_or_network(self):
        with temporary_directory() as tmp:
            first, second = Path(tmp) / "one", Path(tmp) / "two"
            with patch("subprocess.Popen", side_effect=AssertionError("no execution")), patch("socket.socket", side_effect=AssertionError("no network")):
                a = builder.build(first)
                b = builder.build(second)
            self.assertEqual(a, b)
            self.assertEqual((first / "index.html").read_bytes(), (second / "index.html").read_bytes())
            self.assertEqual(a["mode"], "local_preview")
            self.assertEqual(a["placeholder_origin"], "https://example.invalid")
            self.assertEqual(len(a["output_sha256"]), 17)

    def test_routes_assets_fragments_and_base_path(self):
        for base in ("/", "/preview/"):
            with self.subTest(base=base), temporary_directory() as tmp:
                output = Path(tmp) / "site"
                builder.build(output, base=base)
                for page in output.rglob("*.html"):
                    document = Links()
                    document.feed(page.read_text(encoding="utf-8"))
                    for url in document.urls:
                        parsed = urlsplit(url)
                        if parsed.scheme or parsed.netloc:
                            self.assertEqual(parsed.scheme, "https")
                            continue
                        if not parsed.path:
                            self.assertIn(parsed.fragment, document.ids)
                            continue
                        self.assertTrue(parsed.path.startswith(base), url)
                        target = output / parsed.path.lstrip("/")
                        if parsed.path.endswith("/"):
                            target /= "index.html"
                        self.assertTrue(target.is_file(), f"{page}: {url}")
                        if parsed.fragment:
                            linked = Links()
                            linked.feed(target.read_text(encoding="utf-8"))
                            self.assertIn(parsed.fragment, linked.ids)

    def test_local_metadata_does_not_advertise_domain_or_demo(self):
        with temporary_directory() as tmp:
            output = Path(tmp) / "site"
            builder.build(output)
            for page in output.rglob("*.html"):
                text = page.read_text(encoding="utf-8")
                self.assertIn('content="noindex,nofollow"', text)
                self.assertNotIn('rel="canonical"', text)
                self.assertNotIn("application/ld+json", text)
                self.assertNotIn("https://libreevolve.com", text)
            self.assertEqual((output / "robots.txt").read_text(encoding="utf-8"), "User-agent: *\nDisallow: /\n")
            self.assertIn("no approved live experiment", (output / "index.html").read_text(encoding="utf-8"))
            self.assertFalse((output / "sitemap.xml").exists())

    def test_output_collision_preserves_existing_directory(self):
        with temporary_directory() as tmp:
            output = Path(tmp) / "site"
            builder.build(output)
            before = (output / "index.html").read_bytes()
            with self.assertRaises(ValueError):
                builder.build(output)
            self.assertEqual(before, (output / "index.html").read_bytes())

    def test_raw_html_stays_text_and_links_are_scoped(self):
        routes = builder.load_routes(builder.ROOT)
        text = builder.render_markdown('<script>alert(1)</script>\n\n[Setup](alpha-quickstart.md)', "docs/results.md", routes, builder.ROOT, "/")
        self.assertNotIn("<script>", text)
        self.assertIn("&lt;script&gt;", text)
        self.assertIn('href="/getting-started/"', text)
        for markdown in ("[escape](../../outside.md)", "[network](//example.test/x)", "![image](https://example.test/x.png)"):
            with self.subTest(markdown=markdown), self.assertRaises(ValueError):
                builder.render_markdown(markdown, "docs/results.md", routes, builder.ROOT, "/")

    def test_invalid_base_and_duplicate_route_rejected_before_write(self):
        for value in ("//example.test/", "/../", "/x", "/%2e%2e/", "https://example.test/"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                builder.base_path(value)
        with temporary_directory() as tmp:
            output = Path(tmp) / "site"
            routes = builder.load_routes(builder.ROOT)
            with patch.object(builder, "read_source", return_value=json.dumps([routes[0], routes[0]])):
                with self.assertRaises(ValueError):
                    builder.build(output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
