import unittest

import json_utils
import test_utils

class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.input_paths = {
            'about': 'referenced/about.json',
            'agents': 'referenced/agents.json',
            'biomarkers': 'referenced/biomarkers.json',
            'contributions': 'referenced/contributions.json',
            'diseases': 'referenced/diseases.json',
            'documents': 'referenced/documents.json',
            'genes': 'referenced/genes.json',
            'indications': 'referenced/indications.json',
            'organizations': 'referenced/organizations.json',
            'propositions': 'referenced/propositions.json',
            'statements': 'referenced/statements.json',
            'therapies': 'referenced/therapies.json'
        }

        # Load all JSON data once for use in tests
        cls.data = {}
        for key, value in cls.input_paths.items():
            cls.data[key] = json_utils.load(file=value)


class TestDataIntegrity(Base):
    def test_url_matches_document(self):
        # Logic to check if URL within citation matches the document URL
        pass

    def test_publication_date_consistency(self):
        # Logic to ensure publication date in citation matches publication date field
        pass

    def test_no_mismatch_between_document_and_statement(self):
        # Logic to check for mismatches between documents in indications and statements
        pass

    def test_missing_id_values(self):
        # Logic to check for missing ID values
        pass


class TestDateConsistency(Base):
    def test_accessed_date_vs_publication_date(self):
        # Logic to ensure accessed date is equal to or more recent than publication date
        pass

    def test_last_updated_vs_first_published(self):
        # Logic to check if last_updated dates come before first published dates
        pass

    def test_document_access_date(self):
        # Logic to ensure document access date is earlier than first published
        pass


class TestFormatting(Base):
    def test_ending_periods(self):
        # Logic to ensure all indications and descriptions end with periods
        pass

    def test_spelling_errors(self):
        # Logic to print all strings and value counts to look for misspellings
        pass

    def test_trailing_spaces(self):
        # Logic to check for trailing spaces in indications or descriptions
        tests = [
            # tuples of file (records; list[dict]) and key for each record in records
            # the key should be present in each record
            ('agents', 'label'),
            ('biomarkers', 'label'),
            ('contributions', 'description'),
            ('diseases', 'label'),
            ('documents', 'access_date'),
            ('documents', 'citation'),
            ('documents', 'company'),
            ('documents', 'drug_name_brand'),
            ('documents', 'drug_name_generic'),
            ('documents', 'drug_name_generic'),
            ('documents', 'first_published'),
            ('documents', 'label'),
            ('documents', 'publication_date'),
            ('documents', 'url'),
            ('documents', 'url_drug'),
            ('genes', 'label'),
            ('indications', 'indication'),
            ('indications', 'initial_approval_date'),
            ('indications', 'initial_approval_url'),
            ('indications', 'description'),
            ('indications', 'raw_biomarkers'),
            ('indications', 'raw_cancer_type'),
            ('indications', 'raw_therapeutics'),
            ('organizations', 'label'),
            ('organizations', 'last_updated'),
            ('organizations', 'description'),
            ('organizations', 'url'),
            ('propositions', 'description'),
            ('statements', 'direction'),
            ('statements', 'evidence'),
            ('therapies', 'therapy_name'),
            ('therapies', 'therapy_strategy'),
            ('therapies', 'therapy_type')
        ]

        for record_type, key in tests:
            with self.subTest(record_type=record_type, key=key):
                failed_records = test_utils.Test.find_trailing_spaces(records=self.data[record_type], key=key)
                if failed_records:
                    failed_record_ids = ", ".join(str(failed_record) for failed_record in failed_records)
                    self.fail(
                        f"Trailing spaces detected.\n"
                        f"  - File: {record_type}\n"
                        f"  - Key: {key}\n"
                        f"  - Affected IDs: {failed_record_ids}\n"
                        f"  - Total affected: {len(failed_records)}"
                    )

    def test_utf8_characters(self):
        # Logic to search for non-standard UTF-8 characters
        pass


class TestReferenceOrdering(unittest.TestCase):
    def test_order_by_alphabetic_labels(self):
        # Logic to ensure therapy and biomarkers are in alphabetical order
        pass


if __name__ == '__main__':
    unittest.main()
