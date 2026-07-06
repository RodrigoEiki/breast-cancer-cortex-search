import unittest

from src.processing.text import extract_html_text, normalize_whitespace


class ProcessingTests(unittest.TestCase):
    def test_normalize_whitespace(self):
        self.assertEqual(normalize_whitespace("A   B\n\n\nC"), "A B\n\nC")

    def test_extract_html_text_ignores_script(self):
        body = b"<html><head><title>T</title><script>x()</script></head><body><h1>Hello</h1></body></html>"
        text, title = extract_html_text(body)
        self.assertEqual(title, "T")
        self.assertIn("Hello", text)
        self.assertNotIn("x()", text)

if __name__ == "__main__":
    unittest.main()
