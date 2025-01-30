import unittest

import json_utils # Local import

class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Import json files from referenced/ and make them available to inherited test classes
        """
        cls.input_paths = {
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
    """
    Assess that there are no errors with data entry
    """

    def test_document_url_matches_citation(self):
        """
        Assess if `url` field matches the url contained in the `citation` for documents where the url should be
        contained within the citation.Currently, this is relevant for documents where the subtype is one of the
        following:
            - Regulatory approval
        """
        relevant_subtypes = [
            'Regulatory approval'
        ]
        relevant_records = [record for record in self.data['documents'] if record['subtype'] in relevant_subtypes]
        with self.subTest():
            failed_records = [record for record in relevant_records if record['url'] not in record['citation']]
            if failed_records:
                failed_record_ids = ", ".join(str(record['id']) for record in failed_records)
                self.fail(
                    f"URL mismatch between url key value and url contained within citation detected.\n"
                    f"  - Affected ID(s): {failed_record_ids}\n"
                    f"  - Total affected: {len(failed_records)}"
                )

    def test_no_mismatch_between_document_for_indication_and_statement(self):
        """
        Assess if document associated with indications and associated statements differ
        """
        with self.subTest():
            for statement in self.data['statements']:
                statement_documents = statement['reportedIn']
                proposition = json_utils.fetch_records_by_key_value(
                    records=self.data['propositions'],
                    key='id',
                    value=statement['proposition_id']
                )
                proposition = proposition[0]

                indication = json_utils.fetch_records_by_key_value(
                    records=self.data['indications'],
                    key='id',
                    value=proposition['indication_id']
                )
                indication = indication[0]

                if indication['document_id'] not in statement_documents:
                    self.fail(
                        f"Document ID mismatch between indication and statement detected.\n"
                        f"  - Affected ID(s): statement {statement['id']} and indication {indication['id']}"
                    )

    def test_missing_id_values(self):
        """
        Assess if any id values are missing from any referenced records
        """
        for record_type, records in self.data.items():
            with self.subTest(record_type=record_type):
                idx_values = [record['id'] for record in records]
                idx_range = list(range(0, len(records)))
                if not idx_values == idx_range:
                    missing_ids = [idx for idx in idx_range if idx not in idx_values]
                    missing_ids_str = ", ".join(str(idx) for idx in missing_ids)
                    self.fail(
                        f"Missing id values detected.\n"
                        
                        f"  - Affected ID(s): {missing_ids_str}\n"
                        f"  - Total affected: {len(missing_ids)}"
                    )


class TestDateConsistency(Base):
    """
    Assess that various keys containing values for dates align as they should
    """
    def test_document_accessed_date_vs_publication_date(self):
        """
        Assess that the accessed date is more recent than the publication date for each document
        """
        with self.subTest():
            failed_records = [document for document in self.data['documents'] if not (document['access_date'] >= document['publication_date'])]
            if failed_records:
                failed_record_ids = ", ".join(str(record['id']) for record in failed_records)
                self.fail(
                    f"Access date before publication date detected.\n"
                    f"  - File: documents\n"
                    f"  - Affected ID(s): {failed_record_ids}\n"
                    f"  - Total affected: {len(failed_records)}"
                )

    def test_last_updated_vs_first_published(self):
        # Logic to check if last_updated dates come before first published dates
        pass

    def test_document_access_date(self):
        # Logic to ensure document access date is earlier than first published
        pass

    def test_publication_date_consistency(self):
        # Logic to ensure publication date in citation matches publication date field
        pass


class TestFormatting(Base):
    def test_ending_periods(self):
        """
        Ensure that all indications and descriptions end with periods
        """
        # tuples of file (records; list[dict]) and key for each record in records
        tests = [
            ('indications', 'description'),
            ('indications', 'indication')
        ]

        for record_type, key in tests:
            with self.subTest(record_type=record_type, key=key):
                failed_records = []
                for record in self.data[record_type]:
                    if record[key][-1] != '.':
                        failed_records.append(record['id'])

                if failed_records:
                    failed_record_ids = ", ".join(str(record_id) for record_id in failed_records)
                    self.fail(
                        f"Descriptions and indications that do not end with a period detected.\n"
                        f"  - File: {record_type}\n"
                        f"  - Key: {key}\n"
                        f"  - Affected ID(s): {failed_record_ids}\n"
                        f"  - Total affected: {len(failed_records)}"
                    )

    def test_spelling_errors(self):
        # Logic to print all strings and value counts to look for misspellings
        pass

    def test_trailing_spaces(self):
        """
        Assess if any strings values have trailing spaces in any of the json key pairs
        """
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
            ('indications', 'description'),
            ('indications', 'indication'),
            ('indications', 'initial_approval_date'),
            ('indications', 'initial_approval_url'),
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
                failed_records = []
                for record in self.data[record_type]:
                    if record[key] != record[key].rstrip():
                        failed_records.append(record['id'])

                if failed_records:
                    failed_record_ids = ", ".join(str(failed_record) for failed_record in failed_records)
                    self.fail(
                        f"Trailing spaces detected.\n"
                        f"  - File: {record_type}\n"
                        f"  - Key: {key}\n"
                        f"  - Affected ID(s): {failed_record_ids}\n"
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
