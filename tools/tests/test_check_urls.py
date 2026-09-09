import unittest
from tools.check_urls import url_to_site_path, expected_paths

class UrlMapTest(unittest.TestCase):
    def test_root(self):
        self.assertEqual(url_to_site_path("https://systemsguild.eu/"), "_site/index.html")
    def test_slug(self):
        self.assertEqual(url_to_site_path("https://systemsguild.eu/followership"), "_site/followership/index.html")
    def test_nested_with_trailing_slash(self):
        self.assertEqual(url_to_site_path("https://systemsguild.eu/events/"), "_site/events/index.html")
    def test_expected_paths_parses_summary(self):
        text = "== post: 1 urls\nhttps://systemsguild.eu/a\n== page: 1 urls\nhttps://systemsguild.eu/\n"
        self.assertEqual(expected_paths(text), ["_site/a/index.html", "_site/index.html"])

if __name__ == "__main__":
    unittest.main()
