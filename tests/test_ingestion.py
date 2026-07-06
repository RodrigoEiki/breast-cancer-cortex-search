import unittest
import xml.etree.ElementTree as ET

from src.ingestion.clinical_trials import is_breast_cancer_study, trial_to_document
from src.ingestion.pubmed import pubmed_article_to_document


class IngestionTests(unittest.TestCase):
    def test_clinical_trial_conversion(self):
        source = {
            "source_name": "ClinicalTrials.gov Breast Cancer Studies",
            "source_tier": 1,
            "document_type": "clinical_trial",
            "audience": "clinician",
            "topic": "clinical_trials",
            "jurisdiction": "global",
        }
        study = {
            "protocolSection": {
                "identificationModule": {"nctId": "NCT1", "briefTitle": "Breast Cancer Trial"},
                "statusModule": {"overallStatus": "RECRUITING"},
                "conditionsModule": {"conditions": ["Breast Cancer"]},
                "descriptionModule": {"briefSummary": "Summary"},
            }
        }
        self.assertTrue(is_breast_cancer_study(study))
        doc = trial_to_document(source, study, "2026-01-01T00:00:00+00:00")
        self.assertEqual(doc["nct_id"], "NCT1")
        self.assertIn("Breast Cancer Trial", doc["content"])

    def test_pubmed_conversion(self):
        source = {
            "source_name": "PubMed Breast Cancer Research Abstracts",
            "source_tier": 2,
            "document_type": "research_abstract",
            "audience": "researcher",
            "topic": "research",
            "jurisdiction": "global",
        }
        xml = """
        <PubmedArticle>
          <MedlineCitation>
            <PMID>123</PMID>
            <Article>
              <ArticleTitle>Breast cancer review</ArticleTitle>
              <Journal><Title>Journal</Title><JournalIssue><PubDate><Year>2026</Year></PubDate></JournalIssue></Journal>
              <Abstract><AbstractText>Abstract text.</AbstractText></Abstract>
            </Article>
          </MedlineCitation>
          <PubmedData><ArticleIdList><ArticleId IdType="doi">10/example</ArticleId></ArticleIdList></PubmedData>
        </PubmedArticle>
        """
        article = ET.fromstring(xml)
        doc = pubmed_article_to_document(source, article, "2026-01-01T00:00:00+00:00")
        self.assertEqual(doc["pmid"], "123")
        self.assertEqual(doc["doi"], "10/example")
        self.assertIn("Abstract text", doc["content"])


if __name__ == "__main__":
    unittest.main()

