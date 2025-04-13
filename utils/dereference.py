import argparse

import json_utils # Local import


class BaseTable:
    """
    A base class for managing and dereferencing records across database tables. This class provides common
    functionality for dereferencing keys that reference other tables. It serves as a template for specific table
    classes, which inherit from BaseTable and implement additional table-specific logic.

    Attributes:
        records (list[dict]): list of dictionaries that represent one table within the relational database.
    """

    def __init__(self, records: list[dict]):
        """
        Initializes the BaseTable with a list of records.

        Args:
            records (list[dict]): list of dictionaries that represent one table within the relational database.
        """
        self.records = records

    @staticmethod
    def dereference_single(record: dict, referenced_key: str, referenced_records: list[dict]) -> None:
        """
        Dereferences a key for each record in records, where the key's value references a single record.

        Args:
            record (dict): the dictionary that contains a key to dereference.
            referenced_key (str): name of the key in `records` to dereference.
            referenced_records (list[dict]): list of dictionaries that the `referenced_key` refers to.

        Raises:
            KeyError: If the referenced_key is not found in a record.
        """
        if referenced_key not in record:
            raise KeyError(f"Key '{referenced_key}' not found in {record}.")

        referenced_record = json_utils.fetch_records_by_key_value(
            records=referenced_records,
            key='id',
            value=record[referenced_key]
        )

        record[referenced_key] = referenced_record

    @staticmethod
    def dereference_list(record: dict, referenced_key: str, referenced_records: list[dict], key_always_present: bool = True) -> None:
        """
        Dereferences a key for a provided `record`, where the key's value is of type List that references multiple records in another table.

        Args:
            record (dict): the dictionary that contains a key to dereference.
            referenced_key (str): name of the key in `record` to dereference.
            referenced_records (str): list of dictionaries that the `referenced_key` refers to.
            key_always_present (bool): If True, the `referenced_key` is present in all records.

        Raises:
            KeyError: If the `referenced_key` is not found in a record when `key_always_present` is True.
        """
        if key_always_present and (referenced_key not in record):
            raise KeyError(f"Key '{referenced_key}' not found but should be found in {record}")

        if referenced_key not in record:
            pass
        else:
            _values = []
            for value in record[referenced_key]:
                _value = json_utils.fetch_records_by_key_value(
                    records=referenced_records,
                    key='id',
                    value=value
                )
                _values.append(_value)
            record[referenced_key] = _values

    @staticmethod
    def replace_key(record: dict, old_key: str, new_key: str) -> None:
        """
        Dereferences a key for each record in records, where the key's value references a single record.

        Args:
            record (dict): the dictionary that contains a key to replace.
            old_key (str): the name of the key in `record` to replace.
            new_key (str): the new key name that will replace `old_key` in `record`.

        Raises:
            KeyError: If the `old_key` is not found in the record.
        """
        if old_key not in record:
            raise KeyError(f"Key '{old_key}' not found in {record}")

        record[new_key] = record.pop(old_key)

    @staticmethod
    def remove_key(record: dict, key: str) -> None:
        """
        Removes a key from the provided dictionary.

        Args:
            record (dict): the dictionary that contains a key to remove.
            key (str): name of the key in `record` to remove.

        Raises:
            KeyError: If the `key` is not found in `record`.
        """
        if key not in record:
            raise KeyError(f"Key '{key}' not found in {record}")
        record.pop(key)

class Agents(BaseTable):
    """
    Represents the Agents table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table does not currently reference any other tables.

    Attributes:
        records (list[dict]): A list of dictionaries representing the agent records.
    """

    pass

class Biomarkers(BaseTable):
    """
    Represents the Biomarkers table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Genes (initial key: `genes`, resulting key: `genes`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the biomarker records.
    """

    def dereference(self, genes: 'Genes') -> None:
        """Dereference all keys for this table."""
        self.dereference_genes(genes=genes)

    def dereference_genes(self, genes: 'Genes') -> None:
        """
        Dereferences the `genes` key in each biomarker record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `genes` key within each record. This key is not expected to be present within each record, so no KeyError will
        be raised if it is missing.

        Args:
            genes (Genes): An instance of the Genes class representing the genes table.
        """
        for record in self.records:
            self.dereference_list(
                record=record,
                referenced_key='genes',
                referenced_records=genes.records,
                key_always_present=False
            )

class Codings(BaseTable):
    """
        Represents the Codings table. This class inherits common functionality from the BaseTable class and
        dereferences keys that reference other tables. This table does not currently reference any other tables.

        Attributes:
            records (list[dict]): A list of dictionaries representing the coding records.
        """

    pass

class Contributions(BaseTable):
    """
    Represents the Contributions table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Agents (initial key: `agent_id`, resulting key: `agents`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the contribution records.
    """
    def dereference(self, agents: 'Agents') -> None:
        """Dereference all keys for this table."""
        self.dereference_agents(agents=agents)

    def dereference_agents(self, agents: 'Agents') -> None:
        """
        Dereferences the `agent_id` key in each contribution record.

        Utilizes the `dereference_single` function from the BaseTable class to replace the value associated with the
        `agent_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            agents (Agents): An instance of the Agents class representing the agents table.

        Raises:
            KeyError: If the referenced_key, `agent_id`, is not found in a record.
        """
        for record in self.records:
            self.dereference_single(
                record=record,
                referenced_key='agent_id',
                referenced_records=agents.records
            )
            self.replace_key(
                record=record,
                old_key='agent_id',
                new_key='agent'
            )

class Diseases(BaseTable):
    """
    Represents the Diseases table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Codings (initial key: `primary_coding_id`, resulting_key: `primaryCoding`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the therapy records.
    """

    def dereference(self, codings: 'Codings') -> None:
        self.dereference_codings(codings=codings)

    def dereference_codings(self, codings: 'Codings') -> None:
        """
        Dereferences the `primary_coding_id` key in each strength record.

        Utilizes the `dereference_single` function from the BaseTable class to replace the value associated with the
        `primary_coding_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            codings (Codings): An instance of the Codings class representing the codings table.

        Raises:
            KeyError: If the referenced_key, `primary_coding_id`, is not found in a record.
        """
        for record in self.records:
            self.dereference_single(
                record=record,
                referenced_key='primary_coding_id',
                referenced_records=codings.records
            )
            self.replace_key(
                record=record,
                old_key='primary_coding_id',
                new_key='primaryCoding'
            )

class Documents(BaseTable):
    """
    Represents the Documents table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Organizations (initial key: `organization_id`, resulting key: `organization`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the document records.
    """

    def dereference(self, organizations: 'Organizations') -> None:
        """Dereference all keys for this table."""
        self.dereference_organizations(organizations=organizations)

    def dereference_organizations(self, organizations: 'Organizations') -> None:
        """
        Dereferences the `organization_id` key in each document record.

        Utilizes the `dereference_single` function from the BaseTable class to replace the value associated with the
        `organization_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            organizations (Organizations): An instance of the Organizations class representing the organizations table.

        Raises:
            KeyError: If the referenced_key, `organization_id`, is not found in a record.
        """
        for record in self.records:
            self.dereference_single(
                record=record,
                referenced_key='organization_id',
                referenced_records=organizations.records
            )
            self.replace_key(
                record=record,
                old_key='organization_id',
                new_key='organization'
            )

class Genes(BaseTable):
    """
    Represents the Genes table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Codings (initial key: `primary_coding_id`, resulting_key: `primaryCoding`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the therapy records.
    """

    def dereference(self, codings: 'Codings') -> None:
        self.dereference_codings(codings=codings)

    def dereference_codings(self, codings: 'Codings') -> None:
        """
        Dereferences the `primary_coding_id` key in each strength record.

        Utilizes the `dereference_single` function from the BaseTable class to replace the value associated with the
        `primary_coding_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            codings (Codings): An instance of the Codings class representing the codings table.

        Raises:
            KeyError: If the referenced_key, `primary_coding_id`, is not found in a record.
        """
        for record in self.records:
            self.dereference_single(
                record=record,
                referenced_key='primary_coding_id',
                referenced_records=codings.records
            )
            self.replace_key(
                record=record,
                old_key='primary_coding_id',
                new_key='primaryCoding'
            )

class Indications(BaseTable):
    """
    Represents the Indications table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Documents (initial key: `document_id`, resulting key: `document`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the indication records.
    """

    def dereference(self, documents: 'Documents', organizations: 'Organizations') -> None:
        """Dereference all keys for this table."""
        self.dereference_documents(documents=documents, organizations=organizations)

    def dereference_documents(self, documents: 'Documents', organizations: 'Organizations') -> None:
        """
        Dereferences the `document_id` key in each indication record.

        Utilizes the `dereference` function from the Documents class to ensure that each document record is
        fully dereferenced.

        Utilizes the `dereference_single` function from the BaseTable class to replace the value associated with the
        `document_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            documents (Documents): An instance of the Documents class representing the documents table.
            organizations (Organizations): An instance of the Organizations class representing the organizations table.
            dereference_organizations (bool): If `dereference_organizations` is `True`, this function will dereference organizations.

        Raises:
            KeyError: If the referenced_key, `document_id`, is not found in a record.
        """
        documents.dereference(organizations=organizations)

        for record in self.records:
            self.dereference_single(
                record=record,
                referenced_key='document_id',
                referenced_records=documents.records
            )
            self.replace_key(
                record=record,
                old_key='document_id',
                new_key='document'
            )

class Mappings(BaseTable):
    """
    Represents the Mappings table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Codings (initial key: `coding_id`, resulting key: `coding`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the contribution records.
    """
    def dereference(self, codings: 'Codings') -> None:
        """Dereference all keys for this table."""
        self.dereference_codings(codings=codings)

    def dereference_codings(self, codings: 'Codings') -> None:
        """
        Dereferences the `coding_id` key in each coding record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `coding_id` key within each record. This key is not expected to be present within each record, so no KeyError will
        be raised if it is missing.

        Args:
            codings (Codings): An instance of the Codings class representing the codings table.
        """
        for record in self.records:
            self.dereference_single(
                record=record,
                referenced_key='coding_id',
                referenced_records=codings.records
            )
            self.replace_key(
                record=record,
                old_key='coding_id',
                new_key='coding'
            )
            self.remove_key(
                record=record,
                key='id'
            )
            self.remove_key(
                record=record,
                key='primary_coding_id'
            )

class Organizations(BaseTable):
    """
    Represents the Organizations table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table does not currently reference any other tables.

    Attributes:
        records (list[dict]): A list of dictionaries representing the organizations table.
    """

    pass

class Propositions(BaseTable):
    """
    Represents the Propositions table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Biomarkers (initial key: `biomarkers`, resulting key: `biomarkers`)
    - Diseases (initial key: `conditionQualifier_id`, resulting key: `conditionQualifier`)
    - Therapies (initial key: `therapy_id` and `therapy_group_id, resulting key: `objectTherapeutic`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the proposition records.
    """

    def dereference(self, biomarkers: 'Biomarkers', diseases: 'Diseases', genes: 'Genes', therapies: 'Therapies', therapy_groups: 'TherapyGroups') -> None:
        """Dereferences all keys for this table."""
        self.dereference_biomarkers(biomarkers=biomarkers, genes=genes)
        self.dereference_diseases(diseases=diseases)
        self.dereference_therapeutics(therapies=therapies, therapy_groups=therapy_groups)

    def dereference_biomarkers(self, biomarkers: 'Biomarkers', genes: 'Genes') -> None:
        """
        Dereferences the `biomarkers` key in each proposition record.

        Utilizes the `dereference` function from the Biomarkers class to ensure that each biomarker record is
        fully dereferenced.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `biomarkers` key within each record. This key is expected to be present within each record, so a KeyError will
        be raised if it is missing.

        Args:
            biomarkers (Biomarkers): An instance of the Biomarkers class representing the biomarkers table.
            genes (Genes): An instance of the Genes class representing the genes table.

        Raises:
            KeyError: If the referenced_key, `biomarkers`, is not found in a record.
        """
        biomarkers.dereference(genes=genes)

        for record in self.records:
            self.dereference_list(
                record=record,
                referenced_key='biomarkers',
                referenced_records=biomarkers.records,
                key_always_present=True
            )

    def dereference_diseases(self, diseases: 'Diseases') -> None:
        """
        Dereferences the `conditionQualifier_id` key in each proposition record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `conditionQualifier_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            diseases (Diseases): An instance of the Diseases class representing the diseases table.

        Raises:
            KeyError: If the referenced_key, `conditionQualifier_id`, is not found in a record.
        """
        for record in self.records:
            self.dereference_single(
                record=record,
                referenced_key='conditionQualifier_id',
                referenced_records=diseases.records
            )
            self.replace_key(
                record=record,
                old_key='conditionQualifier_id',
                new_key='conditionQualifier'
            )

    def dereference_therapeutics(self, therapies: 'Therapies', therapy_groups: 'TherapyGroups') -> None:
        """
        Dereferences the `therapy_id` key or `therapy_group_id` key in each proposition record.

        Utilizes the `dereference` function from the TherapyGroups class to ensure that each therapy group record is
        fully dereferenced.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `objectTherapeutic` key within each record.

        Args:
            therapies (Therapies): list of dictionaries to dereference `therapy_ids` against.
            therapy_groups (TherapyGroups): list of dictionaries to dereference `therapy_group_ids` against.

        Raises:
            KeyError: If neither referenced_key values, `therapy_id` or `therapy_group_id, are not found in a record.
        """
        therapy_groups.dereference(therapies=therapies)

        for record in self.records:
            if isinstance(record['therapy_id'], int):
                self.dereference_single(
                    record=record,
                    referenced_key='therapy_id',
                    referenced_records=therapies.records
                )
                self.replace_key(
                    record=record,
                    old_key='therapy_id',
                    new_key='objectTherapeutic'
                )
                self.remove_key(
                    record=record,
                    key='therapy_group_id'
                )
            elif isinstance(record['therapy_group_id'], int):
                self.dereference_single(
                    record=record,
                    referenced_key='therapy_group_id',
                    referenced_records=therapy_groups.records
                )
                self.replace_key(
                    record=record,
                    old_key='therapy_group_id',
                    new_key='objectTherapeutic'
                )
                self.remove_key(
                    record=record,
                    key='therapy_id'
                )
            else:
                raise KeyError(f"Neither 'therapy_id' nor 'therapy_group_id' are keys found in {record}")

class Statements(BaseTable):
    """
    Represents the Statements table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Contributions (initial key: `contributions`, resulting key: `contributions`)
    - Documents (initial key: `reportedIn`, resulting key: `reportedIn`)
    - Indications (initial key: `indication_id, resulting key: `indication`)
    - Propositions (initial key: `proposition_id`, resulting key: `proposition`)
    - Strengths (initial key: `strength_id`, resulting key: `strength`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the statement records.
    """

    def dereference(self, agents: 'Agents', biomarkers: 'Biomarkers', codings: 'Codings', contributions: 'Contributions', diseases: 'Diseases', documents: 'Documents', genes: 'Genes', indications: 'Indications', mappings: 'Mappings', organizations: 'Organizations', propositions: 'Propositions', therapies: 'Therapies', therapy_groups: 'TherapyGroups') -> None:
        """Dereferences all keys for this table."""
        self.dereference_contributions(contributions=contributions, agents=agents)
        self.dereference_documents(documents=documents, organizations=organizations)
        self.dereference_indications(indications=indications, documents=documents, organizations=organizations)
        self.dereference_propositions(propositions=propositions, biomarkers=biomarkers, diseases=diseases, genes=genes, therapies=therapies, therapy_groups=therapy_groups)

    def dereference_contributions(self, contributions: 'Contributions', agents: 'Agents') -> None:
        """
        Dereferences the `contributions` key in each statement record.

        Utilizes the `dereference` function from the Contributions class to ensure that each contribution record is
        fully dereferenced.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `contributions` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            agents (Agents): An instance of the Agents class representing the agents table.
            contributions (Contributions): An instance of the Contributions class representing the Contributions table.

        Raises:
            KeyError: If the referenced_key, `contributions`, is not found in a record.
        """
        contributions.dereference(agents=agents)

        for record in self.records:
            self.dereference_list(
                record=record,
                referenced_key='contributions',
                referenced_records=contributions.records,
                key_always_present=True
            )

    def dereference_documents(self, documents: 'Documents', organizations: 'Organizations') -> None:
        """
        Dereferences the `reportedIn` key in each statement record.

        Utilizes the `dereference` function from the Documents class to ensure that each document record is
        fully dereferenced.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `reportedIn` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            documents (Documents): An instance of the Documents class representing the documents table.
            organizations (Organizations): An instance of the Organizations class representing the organizations table.

        Raises:
            KeyError: If the referenced_key, `reportedIn`, is not found in a record.
        """
        documents.dereference(organizations=organizations)

        for record in self.records:
            self.dereference_list(
                record=record,
                referenced_key='reportedIn',
                referenced_records=documents.records,
                key_always_present=True
            )

    def dereference_indications(self, indications: 'Indications', documents: 'Documents', organizations: 'Organizations') -> None:
        """
        Dereferences the `indication_id` key in each statement record.

        Utilizes the `dereference` function from the Indications class to ensure that each indication record is
        fully dereferenced.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `indication_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.
        Note: This will eventually not be expected to be present within each record, once we add more than regulatory approvals.

        Args:
            indications (Indications): An instance of the Indications class representing the indications table.
            documents (Documents): An instance of the Documents class representing the documents table.
            organizations (Organizations): An instance of the Organizations class representing the organizations table.

        Raises:
            KeyError: If the referenced_key, `indication_id`, is not found in a record.
        """

        # Documents will have already been dereferenced for organizations
        # instead of using the function from the Indications class, we will just manually
        # dereference documents for indications

        for record in indications.records:
            self.dereference_single(
                record=record,
                referenced_key='document_id',
                referenced_records=documents.records
            )
            self.replace_key(
                record=record,
                old_key='document_id',
                new_key='document'
            )

        # indications.dereference(documents=documents, organizations=organizations)

        for record in self.records:
            self.dereference_single(
                record=record,
                referenced_key='indication_id',
                referenced_records=indications.records
            )
            self.replace_key(
                record=record,
                old_key='indication_id',
                new_key='indication'
            )

    def dereference_propositions(self, propositions: 'Propositions', biomarkers: 'Biomarkers', diseases: 'Diseases', genes: 'Genes', therapies: 'Therapies', therapy_groups: 'TherapyGroups') -> None:
        """
        Dereferences the `proposition_id` key in each statement record.

        Utilizes the `dereference` function from the Propositions class to ensure that each proposition record is
        fully dereferenced.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `proposition_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            propositions (Propositions): An instance of the Propositions class representing the propositions table.
            biomarkers (Biomarkers): An instance of the Biomarkers class representing the biomarkers table.
            diseases (Diseases): An instance of the Diseases class representing the diseases table.
            genes (Genes): An instance of the Genes class representing the genes table.
            therapies (Therapies): An instance of the Therapies class representing the therapies table.
            therapy_groups (TherapyGroups): An instance of the TherapyGroups class representing the therapy_groups table.

        Raises:
            KeyError: If the referenced_key, `proposition_id`, is not found in a record.
        """
        propositions.dereference(
            biomarkers=biomarkers,
            diseases=diseases,
            genes=genes,
            therapies=therapies,
            therapy_groups=therapy_groups
        )

        for record in self.records:
            self.dereference_single(
                record=record,
                referenced_key='proposition_id',
                referenced_records=propositions.records
            )
            self.replace_key(
                record=record,
                old_key='proposition_id',
                new_key='proposition'
            )

    def dereference_strengths(self, strengths: 'Strengths') -> None:
        """
        Dereferences the `strength_id` key in each statement record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `strength_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            strengths (Strengths): An instance of the Strengths class representing the strengths table.

        Raises:
            KeyError: If the referenced_key, `strength_id`, is not found in a record.
        """
        for record in self.records:
            self.dereference_single(
                record=record,
                referenced_key='strength_id',
                referenced_records=strengths.records
            )
            self.replace_key(
                record=record,
                old_key='strength_id',
                new_key='strength'
            )

class Strengths(BaseTable):
    """
    Represents the Strengths table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Codings (initial key: `primary_coding_id`, resulting_key: `primaryCoding`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the therapy records.
    """

    def dereference(self, codings: 'Codings') -> None:
        self.dereference_codings(codings=codings)

    def dereference_codings(self, codings: 'Codings') -> None:
        """
        Dereferences the `primary_coding_id` key in each strength record.

        Utilizes the `dereference_single` function from the BaseTable class to replace the value associated with the
        `primary_coding_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            codings (Codings): An instance of the Codings class representing the codings table.

        Raises:
            KeyError: If the referenced_key, `primary_coding_id`, is not found in a record.
        """
        for record in self.records:
            self.dereference_single(
                record=record,
                referenced_key='primary_coding_id',
                referenced_records=codings.records
            )
            self.replace_key(
                record=record,
                old_key='primary_coding_id',
                new_key='primaryCoding'
            )

class Therapies(BaseTable):
    """
    Represents the Therapies table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Codings (initial key: `primary_coding_id`, resulting_key: `primaryCoding`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the therapy records.
    """

    def dereference(self, codings: 'Codings') -> None:
        self.dereference_codings(codings=codings)

    def dereference_codings(self, codings: 'Codings') -> None:
        """
        Dereferences the `primary_coding_id` key in each strength record.

        Utilizes the `dereference_single` function from the BaseTable class to replace the value associated with the
        `primary_coding_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            codings (Codings): An instance of the Codings class representing the codings table.

        Raises:
            KeyError: If the referenced_key, `primary_coding_id`, is not found in a record.
        """
        for record in self.records:
            self.dereference_single(
                record=record,
                referenced_key='primary_coding_id',
                referenced_records=codings.records
            )
            self.replace_key(
                record=record,
                old_key='primary_coding_id',
                new_key='primaryCoding'
            )

class TherapyGroups(BaseTable):
    """
    Represents the Therapy Groups table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Therapies (key: `therapies`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the therapy records.
    """

    def dereference(self, therapies: 'Therapies') -> None:
        """Dereference all keys for this table."""
        self.dereference_therapies(therapies=therapies)

    def dereference_therapies(self, therapies: 'Therapies') -> None:
        """
        Dereferences the `therapies_id` key in each therapy group record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `agent_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            therapies (list[dict]): list of dictionaries to dereference against.

        Raises:
            KeyError: If the referenced_key, `therapies`, is not found in a record.
        """
        for record in self.records:
            self.dereference_list(
                record=record,
                referenced_key='therapies',
                referenced_records=therapies.records,
                key_always_present=True
            )

def main(input_paths):
    """
    Creates a single JSON file for the Molecular Oncology Almanac (moalmanac) database by dereferencing
    referenced JSON files. By default, these are located in the referenced/ folder of this repository.

    Args:
        input_paths (dict): Dictionary of paths to referenced JSON files.

    Returns:
        dict: Dereferenced database, with keys:
            - about (dict): Dictionary containing database metadata, from referenced/about.json.
            - content (list[dict]): List of dictionaries containing dereferenced database.
    """

    # Step 1: Read json files
    about = json_utils.load(file=input_paths['about'])
    agents = json_utils.load(file=input_paths['agents'])
    biomarkers = json_utils.load(file=input_paths['biomarkers'])
    codings = json_utils.load(file=input_paths['codings'])
    contributions = json_utils.load(file=input_paths['contributions'])
    diseases = json_utils.load(file=input_paths['diseases'])
    documents = json_utils.load(file=input_paths['documents'])
    genes = json_utils.load(file=input_paths['genes'])
    indications = json_utils.load(file=input_paths['indications'])
    mappings = json_utils.load(file=input_paths['mappings'])
    organizations = json_utils.load(file=input_paths['organizations'])
    propositions = json_utils.load(file=input_paths['propositions'])
    statements = json_utils.load(file=input_paths['statements'])
    therapies = json_utils.load(file=input_paths['therapies'])
    therapy_groups = json_utils.load(file=input_paths['therapy_groups'])

    # Step 2: Generate table objects
    agents = Agents(records=agents)
    biomarkers = Biomarkers(records=biomarkers)
    codings = Codings(records=codings)
    contributions = Contributions(records=contributions)
    diseases = Diseases(records=diseases)
    documents = Documents(records=documents)
    genes = Genes(records=genes)
    indications = Indications(records=indications)
    mappings = Mappings(records=mappings)
    organizations = Organizations(records=organizations)
    propositions = Propositions(records=propositions)
    statements = Statements(records=statements)
    therapies = Therapies(records=therapies)
    therapy_groups = TherapyGroups(records=therapy_groups)

    # Step 3: Dereference the database and generate statements
    statements.dereference(
        agents=agents,
        biomarkers=biomarkers,
        codings=codings,
        contributions=contributions,
        diseases=diseases,
        documents=documents,
        genes=genes,
        indications=indications,
        mappings=mappings,
        organizations=organizations,
        propositions=propositions,
        therapies=therapies,
        therapy_groups=therapy_groups
    )

    return {
        'about': about,
        'content': statements.records
    }

if __name__ =="__main__":
    arg_parser = argparse.ArgumentParser(
        prog='dereference',
        description='dereferences moalmanac db (currently in draft and development).'
    )
    arg_parser.add_argument(
        '--about',
        help='json detailing db metadata',
        default='referenced/about.json'
    ),
    arg_parser.add_argument(
        '--agents',
        help='json detailing agents',
        default='referenced/agents.json'
    ),
    arg_parser.add_argument(
        '--biomarkers',
        help='json detailing db biomarkers',
        default='referenced/biomarkers.json'
    ),
    arg_parser.add_argument(
        '--codings',
        help='json detailing db codings',
        default='referenced/codings.json'
    )
    arg_parser.add_argument(
        '--contributions',
        help='json detailing db contributions',
        default='referenced/contributions.json'
    ),
    arg_parser.add_argument(
        '--diseases',
        help='json detailing db diseases',
        default='referenced/diseases.json'
    ),
    arg_parser.add_argument(
        '--documents',
        help='json detailing db documents',
        default='referenced/documents.json'
    )
    arg_parser.add_argument(
        '--genes',
        help='json detailing db genes',
        default='referenced/genes.json'
    ),
    arg_parser.add_argument(
        '--indications',
        help='json detailing db indications',
        default='referenced/indications.json'
    ),
    arg_parser.add_argument(
        '--mappings',
        help='json detailing db mappings',
        default='referenced/mappings.json'
    )
    arg_parser.add_argument(
        '--organizations',
        help='json detailing db organizations',
        default='referenced/organizations.json'
    ),
    arg_parser.add_argument(
        '--propositions',
        help='json detailing db propositions',
        default='referenced/propositions.json'
    ),
    arg_parser.add_argument(
        '--statements',
        help='json detailing db statements',
        default='referenced/statements.json'
    ),
    arg_parser.add_argument(
        '--therapies',
        help='json detailing db therapies',
        default='referenced/therapies.json'
    )
    arg_parser.add_argument(
        '--therapy-groups',
        help='json detailing db therapy groups',
        default='referenced/therapy_groups.json'
    )
    arg_parser.add_argument(
        '--output',
        help='Output json file',
        default='moalmanac-draft.dereferenced.json'
    )
    args = arg_parser.parse_args()

    input_data = {
        'about': args.about,
        'agents': args.agents,
        'biomarkers': args.biomarkers,
        'codings': args.codings,
        'contributions': args.contributions,
        'diseases': args.diseases,
        'documents': args.documents,
        'genes': args.genes,
        'indications': args.indications,
        'mappings': args.mappings,
        'organizations': args.organizations,
        'propositions': args.propositions,
        'statements': args.statements,
        'therapies': args.therapies,
        'therapy_groups': args.therapy_groups
    }

    dereferenced = main(input_paths=input_data)
    json_utils.write_dict(
        data=dereferenced,
        keys_list=['content'],
        file=args.output
    )
