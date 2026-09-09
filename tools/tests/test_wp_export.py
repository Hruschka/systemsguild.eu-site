import unittest
from tools.wp_export import local_path, UPLOAD_PREFIX

class LocalPathTest(unittest.TestCase):
    def test_maps_upload_url_to_assets(self):
        self.assertEqual(
            local_path("https://systemsguild.eu/wp-content/uploads/2021/06/TrasnIndentedSkull.png"),
            "assets/uploads/2021/06/TrasnIndentedSkull.png")

    def test_protocol_relative_url(self):
        self.assertEqual(local_path("//systemsguild.eu/wp-content/uploads/2018/11/a.jpg"),
                         "assets/uploads/2018/11/a.jpg")

    def test_non_upload_url_returns_none(self):
        self.assertIsNone(local_path("https://example.org/x.png"))

if __name__ == "__main__":
    unittest.main()
