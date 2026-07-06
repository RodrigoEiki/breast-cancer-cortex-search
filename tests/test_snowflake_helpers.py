import unittest

from src.snowflake.cortex import build_context, build_filter, build_prompt, source_label


class SnowflakeHelperTests(unittest.TestCase):
    def test_build_filter_combines_selected_facets(self):
        result = build_filter(["clinical_guidance"], ["screening"], [1])
        self.assertIn("@and", result)

    def test_source_label_prefers_pubmed_identifier(self):
        label = source_label({"TITLE": "Title", "PMID": "123"}, 1)
        self.assertIn("PMID 123", label)

    def test_prompt_contains_context_and_question(self):
        results = [{"TITLE": "Doc", "CONTENT": "Evidence", "SOURCE_NAME": "Source"}]
        prompt = build_prompt("Question?", results)
        self.assertIn("Evidence", prompt)
        self.assertIn("Question?", prompt)
        self.assertIn("retrieved context", prompt)

    def test_build_context_numbers_sources(self):
        context = build_context([{"TITLE": "Doc", "CONTENT": "Text"}])
        self.assertIn("Source [1]", context)


if __name__ == "__main__":
    unittest.main()

