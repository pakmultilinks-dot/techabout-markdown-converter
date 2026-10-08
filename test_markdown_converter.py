"""Tests for markdown_converter.py"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from markdown_converter import build_page, convert_body, inline


class TestMarkdownConverter(unittest.TestCase):
    def test_headings(self):
        self.assertIn("<h1>Title</h1>", convert_body("# Title"))
        self.assertIn("<h2>Sub</h2>", convert_body("## Sub"))
        self.assertIn("<h3>Deep</h3>", convert_body("### Deep"))

    def test_paragraphs(self):
        body = convert_body("First line.\n\nSecond line.")
        self.assertIn("<p>First line.</p>", body)
        self.assertIn("<p>Second line.</p>", body)

    def test_multiline_paragraph_joined(self):
        body = convert_body("line one\nline two")
        self.assertIn("<p>line one line two</p>", body)

    def test_bold_and_italic(self):
        body = convert_body("This is **bold** and *italic*.")
        self.assertIn("<strong>bold</strong>", body)
        self.assertIn("<em>italic</em>", body)

    def test_inline_code(self):
        body = convert_body("Run `pip install x` now.")
        self.assertIn("<code>pip install x</code>", body)

    def test_code_span_protects_markup(self):
        body = convert_body("A `**not bold**` span.")
        self.assertIn("<code>**not bold**</code>", body)
        self.assertNotIn("<strong>", body)

    def test_link(self):
        body = convert_body("Visit [TechAbout](https://techabout.com) today.")
        self.assertIn('<a href="https://techabout.com">TechAbout</a>', body)

    def test_image(self):
        body = convert_body("Logo: ![alt text](logo.png)")
        self.assertIn('<img src="logo.png" alt="alt text">', body)

    def test_fenced_code_block(self):
        body = convert_body("```python\nprint('hi')\n```")
        self.assertIn("<pre><code", body)
        self.assertIn("print(&#x27;hi&#x27;)", body)

    def test_unordered_list(self):
        body = convert_body("- one\n- two\n- three")
        self.assertIn("<ul>", body)
        self.assertIn("<li>one</li>", body)
        self.assertIn("</ul>", body)

    def test_ordered_list(self):
        body = convert_body("1. first\n2. second")
        self.assertIn("<ol>", body)
        self.assertIn("<li>first</li>", body)
        self.assertIn("</ol>", body)

    def test_blockquote(self):
        body = convert_body("> A wise quote")
        self.assertIn("<blockquote>A wise quote</blockquote>", body)

    def test_horizontal_rule(self):
        self.assertIn("<hr>", convert_body("Above\n\n---\n\nBelow"))

    def test_raw_html_escaped(self):
        body = convert_body("Hello <script>alert(1)</script>")
        self.assertIn("&lt;script&gt;", body)
        self.assertNotIn("<script>alert", body)

    def test_inline_formatting_inside_heading(self):
        body = convert_body("# Welcome to **TechAbout**")
        self.assertIn("<h1>Welcome to <strong>TechAbout</strong></h1>", body)

    def test_build_page_structure(self):
        page = build_page("<p>hi</p>", title="Test")
        self.assertTrue(page.startswith("<!DOCTYPE html>"))
        self.assertIn("<title>Test</title>", page)
        self.assertIn("<p>hi</p>", page)
        self.assertIn("</html>", page)

    def test_empty_input(self):
        self.assertEqual(convert_body(""), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
