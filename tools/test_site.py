from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import unittest


ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = [ROOT / "index.html"] + sorted(ROOT.glob("*/index.html"))


def page_name(path):
    return "index.html" if path.parent == ROOT else path.parent.name + ".html"


class PortfolioHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchors = []
        self.headings = []
        self.sources = []
        self.footer_text = []
        self._anchor_stack = []
        self._heading_stack = []
        self._nav_depth = 0
        self._footer_depth = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if attributes.get("src"):
            self.sources.append(attributes["src"])

        if tag == "nav":
            self._nav_depth += 1
        elif tag == "footer":
            self._footer_depth += 1

        if tag == "a":
            anchor = {
                "attrs": attributes,
                "text": [],
                "in_nav": self._nav_depth > 0,
                "in_footer": self._footer_depth > 0,
            }
            self.anchors.append(anchor)
            self._anchor_stack.append(anchor)

        if tag in {"h1", "h2", "h3"}:
            heading = {"tag": tag, "text": []}
            self.headings.append(heading)
            self._heading_stack.append(heading)

    def handle_endtag(self, tag):
        if tag == "a" and self._anchor_stack:
            self._anchor_stack.pop()
        elif tag in {"h1", "h2", "h3"} and self._heading_stack:
            self._heading_stack.pop()

        if tag == "nav":
            self._nav_depth -= 1
        elif tag == "footer":
            self._footer_depth -= 1

    def handle_data(self, data):
        if self._anchor_stack:
            self._anchor_stack[-1]["text"].append(data)
        if self._heading_stack:
            self._heading_stack[-1]["text"].append(data)
        if self._footer_depth:
            self.footer_text.append(data)


def parse_page(path):
    parser = PortfolioHTMLParser()
    parser.feed(path.read_text(encoding="utf-8"))

    for anchor in parser.anchors:
        anchor["text"] = " ".join("".join(anchor["text"]).split())
    for heading in parser.headings:
        heading["text"] = " ".join("".join(heading["text"]).split())
    parser.footer_text = " ".join("".join(parser.footer_text).split())
    return parser


class PortfolioNavigationTests(unittest.TestCase):
    def test_homepage_highlights_link_to_their_detail_pages(self):
        page = parse_page(ROOT / "index.html")
        h2_text = [heading["text"] for heading in page.headings if heading["tag"] == "h2"]
        self.assertIn("Portfolio Highlights", h2_text)
        self.assertNotIn("Impact Highlights", h2_text)

        highlights = {
            anchor["attrs"].get("href"): anchor["text"]
            for anchor in page.anchors
            if "highlight-card" in anchor["attrs"].get("class", "").split()
        }
        self.assertEqual(
            set(highlights),
            {"ulvac-field-service/", "conveyor-sorting/"},
        )
        self.assertIn("View experience", highlights["ulvac-field-service/"])
        self.assertIn("View project", highlights["conveyor-sorting/"])

    def test_every_page_uses_clean_home_links_and_marks_the_active_section(self):
        project_pages = {
            "projects.html",
            "nexa-research.html",
            "seeing-through-occlusion.html",
            "conveyor-sorting.html",
            "autonomous-driving-planner.html",
            "drone-pathing-rl.html",
            "terrain-walker.html",
            "ulvac-field-service.html",
            "paltorc-ebike.html",
        }

        for path in HTML_FILES:
            with self.subTest(page=path.name):
                page = parse_page(path)
                nav_anchors = [anchor for anchor in page.anchors if anchor["in_nav"]]
                brand = [
                    anchor
                    for anchor in nav_anchors
                    if "brand" in anchor["attrs"].get("class", "").split()
                ]
                self.assertEqual(len(brand), 1)
                self.assertEqual(brand[0]["attrs"].get("href"), "./")

                about = [anchor for anchor in nav_anchors if anchor["text"] == "About"]
                self.assertEqual(len(about), 1)
                self.assertEqual(about[0]["attrs"].get("href"), "./")
                self.assertFalse(any(anchor["attrs"].get("href") == "index.html" for anchor in nav_anchors))

                current = [
                    anchor
                    for anchor in nav_anchors
                    if anchor["attrs"].get("aria-current")
                ]
                self.assertEqual(len(current), 1)

                if page_name(path) == "index.html":
                    expected_current = "About"
                    expected_current_type = "page"
                elif page_name(path) == "resume.html":
                    expected_current = "Resume"
                    expected_current_type = "page"
                elif page_name(path) == "projects.html":
                    expected_current = "Projects & Experience"
                    expected_current_type = "page"
                elif page_name(path) in project_pages:
                    expected_current = "Projects & Experience"
                    expected_current_type = "location"
                else:
                    self.fail(f"No active-navigation expectation for {path.name}")

                self.assertEqual(current[0]["text"], expected_current)
                self.assertEqual(
                    current[0]["attrs"].get("aria-current"),
                    expected_current_type,
                )

    def test_every_footer_has_contact_and_profile_links_without_stale_dates(self):
        expected_links = {
            "mailto:leos@andrew.cmu.edu",
            "https://github.com/leos-bit",
            "https://linkedin.com/in/leoshaw",
        }

        for path in HTML_FILES:
            with self.subTest(page=path.name):
                page = parse_page(path)
                footer_links = {
                    anchor["attrs"].get("href")
                    for anchor in page.anchors
                    if anchor["in_footer"]
                }
                self.assertTrue(expected_links.issubset(footer_links))
                self.assertNotIn("Last updated:", page.footer_text)

                if page_name(path) not in {"index.html", "projects.html", "resume.html"}:
                    back_links = [
                        anchor
                        for anchor in page.anchors
                        if anchor["in_footer"]
                        and anchor["attrs"].get("href") == "projects/"
                        and anchor["text"] == "Back to projects & experience"
                    ]
                    self.assertEqual(len(back_links), 1)

    def test_all_local_page_and_asset_targets_exist(self):
        missing = []

        for path in HTML_FILES:
            page = parse_page(path)
            for anchor in page.anchors:
                value = anchor["attrs"].get("href")
                if not value or value.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                local_path = unquote(urlsplit(value).path)
                target = ROOT / ("index.html" if local_path in {"", "./"} else local_path)
                if target.is_dir():
                    target = target / "index.html"
                if not target.exists():
                    missing.append((path.name, value))

            for value in page.sources:
                local_path = unquote(urlsplit(value).path)
                if not (ROOT / local_path).exists():
                    missing.append((path.name, value))

        self.assertEqual(missing, [])

    def test_homepage_does_not_repeat_primary_navigation_as_a_second_section(self):
        page = parse_page(ROOT / "index.html")
        h2_text = [heading["text"] for heading in page.headings if heading["tag"] == "h2"]
        self.assertNotIn("Portfolio Navigation", h2_text)


if __name__ == "__main__":
    unittest.main()
