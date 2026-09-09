import unittest
from tools.convert_posts import html_to_markdown, front_matter, post_filename

SKULL = ('<p>Intro.</p>\n<div class="wp-block-media-text alignwide is-stacked-on-mobile" style="grid-template-columns:15% auto">'
         '<figure class="wp-block-media-text__media"><img loading="lazy" width="680" height="400" '
         'src="https://systemsguild.eu/wp-content/uploads/2021/06/TrasnIndentedSkull.png" alt="" class="wp-image-701 size-full" /></figure>'
         '<div class="wp-block-media-text__content">\n<h4><strong><strong>Teamwork means doing what you’re told.</strong></strong></h4>\n</div></div>\n<p>After.</p>')

class HtmlToMarkdownTest(unittest.TestCase):
    def test_skull_block_becomes_rule_include(self):
        md = html_to_markdown(SKULL)
        self.assertIn('{% include rule.html text="Teamwork means doing what you’re told." %}', md)
        self.assertNotIn("wp-block-media-text", md)
        self.assertIn("Intro.", md)
        self.assertIn("After.", md)

    def test_upload_urls_rewritten(self):
        md = html_to_markdown('<p><img src="https://systemsguild.eu/wp-content/uploads/2025/05/resting.jpg" alt="x"></p>')
        self.assertIn("/assets/uploads/2025/05/resting.jpg", md)
        self.assertNotIn("wp-content", md)

    def test_quotes_in_rule_text_are_escaped(self):
        html = SKULL.replace("Teamwork means doing what you’re told.", 'Say "no" never.')
        self.assertIn('text="Say &quot;no&quot; never."', html_to_markdown(html))

class FrontMatterTest(unittest.TestCase):
    def test_front_matter_fields(self):
        post = {"id": 647, "slug": "the-stepford-hires", "date": "2025-09-29T01:00:00",
                "title": {"rendered": "The Stepford Hires"}, "author": 3, "tags": [17, 14]}
        tags = {17: {"slug": "culture", "name": "#culture"}, 14: {"slug": "hiring", "name": "hiring"}}
        users = {3: "james-robertson"}
        fm = front_matter(post, tags, users)
        self.assertEqual(fm["title"], "The Stepford Hires")
        self.assertEqual(fm["date"], "2025-09-29 01:00:00 +0200")
        self.assertEqual(fm["author"], "james-robertson")
        self.assertEqual(fm["tags"], ["culture", "hiring"])
        self.assertEqual(fm["tag_names"], ["#culture", "hiring"])
        self.assertEqual(fm["permalink"], "/the-stepford-hires/")
        self.assertEqual(fm["wp_id"], 647)

    def test_filename(self):
        self.assertEqual(post_filename({"slug": "followership", "date": "2025-06-02T01:00:00"}),
                         "_posts/2025-06-02-followership.md")

if __name__ == "__main__":
    unittest.main()

class ImageBlockTest(unittest.TestCase):
    def test_floated_image_block_becomes_figure_include(self):
        html = ('<div class="wp-block-image"><figure class="alignright size-large is-resized">'
                '<img src="https://systemsguild.eu/wp-content/uploads/2021/07/resting.jpg" class="wp-image-721" width="175" alt="slack is think time."/></figure></div>'
                '<p>Text.</p>')
        md = html_to_markdown(html)
        self.assertIn('{% include figure.html src="/assets/uploads/2021/07/resting.jpg" alt="slack is think time." align="right" width="175px" %}', md)
        self.assertNotIn("wp-block-image", md)
