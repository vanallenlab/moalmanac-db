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

    def dereference_single(self, referenced_key: str, referenced_records: list[dict], new_key_name: str) -> None:
        """
        Dereferences a key for each record in records, where the key's value references a single record.

        Args:
            referenced_key (str): name of the key in `records` to dereference.
            referenced_records (list[dict]): list of dictionaries that the `referenced_key` refers to.
            new_key_name (str): key to store dereferenced record in `records`. this key replaces `referenced_key`.

        Raises:
            KeyError: If the referenced_key is not found in a record.
        """
        dereferenced_records = []
        for record in self.records:
            if referenced_key not in record:
                raise KeyError(f"Key '{referenced_key}' not found in {record}.")

            referenced_record = json_utils.fetch_records_by_key_value(
                records=referenced_records,
                key='id',
                value=record[referenced_key]
            )

            new_record = {}
            for key, value in record.items():
                if key == referenced_key:
                    new_record[new_key_name] = referenced_record
                else:
                    new_record[key] = value

            dereferenced_records.append(new_record)
        self.records = dereferenced_records

    def dereference_list(self, referenced_key: str, referenced_records: list[dict], key_always_present: bool = True) -> None:
        """
        Dereferences a key for each record in `records`, where the key's value is of type List to reference multiple records.

        Args:
            referenced_key (str): name of the key in `records` to dereference.
            referenced_records (str): list of dictionaries that the `referenced_key` refers to.
            key_always_present (bool): If True, the `referenced_key` is present in all records.

        Raises:
            KeyError: If the `referenced_key` is not found in a record when `key_always_present` is True.
        """
        for record in self.records:
            if key_always_present and (referenced_key not in record):
                raise KeyError(f"Key '{referenced_key}' not found but should be found in {record}")

            if referenced_key not in record:
                continue

            _values = []
            for value in record[referenced_key]:
                _value = json_utils.fetch_records_by_key_value(
                    records=referenced_records,
                    key='id',
                    value=value
                )
                _values.append(_value)
            record[referenced_key] = _values

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
        records (list[dict]): A list of dictionaries representing the document records.
    """

    def dereference_genes(self, genes: list[dict]) -> None:
        """
        Dereferences the `genes` key in each biomarker record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `gene` key within each record. This key is not expected to be present within each record, so no KeyError will
        be raised if it is missing.

        Args:
            genes (list[dict]): list of dictionaries to dereference against.
        """
        self.dereference_list(
            referenced_key='genes',
            referenced_records=genes,
            key_always_present=False
        )

class Contributions(BaseTable):
    """
    Represents the Contributions table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Agents (key: `agent_id`, resulting key: `agents`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the contribution records.
    """

    def dereference_agents(self, agents: list[dict]) -> None:
        """
        Dereferences the `agent_id` key in each contribution record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `agent_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            agents (list[dict]): list of dictionaries to dereference against.

        Raises:
            KeyError: If the referenced_key, `agent_id`, is not found in a record.
        """
        self.dereference_single(
            referenced_key='agent_id',
            referenced_records=agents,
            new_key_name='agent'
        )

class Diseases(BaseTable):
    """
    Represents the Diseases table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table does not currently reference any other tables.

    Attributes:
        records (list[dict]): A list of dictionaries representing the disease records.
    """

    pass

class Documents(BaseTable):
    """
    Represents the Documents table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Organizations (key: `organization_id`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the document records.
    """

    def dereference_organizations(self, organizations: list[dict]) -> None:
        """
        Dereferences the `organization_id` key in each proposition record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `organization_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            organizations (list[dict]): list of dictionaries to dereference against.

        Raises:
            KeyError: If the referenced_key, `organization_id`, is not found in a record.
        """
        self.dereference_single(
            referenced_key='organization_id',
            referenced_records=organizations,
            new_key_name='organization'
        )

class Genes(BaseTable):
    """
    Represents the Genes table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table does not currently reference any other tables.

    Attributes:
        records (list[dict]): A list of dictionaries representing the gene records.
    """

    pass

class Indications(BaseTable):
    """
    Represents the Indications table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Documents (key: `document_id`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the indication records.
    """

    def dereference_documents(self, documents: list[dict]) -> None:
        """
        Dereferences the `document_id` key in each proposition record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `document_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            documents (list[dict]): list of dictionaries to dereference against.

        Raises:
            KeyError: If the referenced_key, `document_id`, is not found in a record.
        """
        self.dereference_single(
            referenced_key='document_id',
            referenced_records=documents,
            new_key_name='document'
        )

class Organizations(BaseTable):
    """
    Represents the Organizations table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table does not currently reference any other tables.

    Attributes:
        records (list[dict]): A list of dictionaries representing the organization records.
    """

    pass

class Propositions(BaseTable):
    """
    Represents the Propositions table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Biomarkers (initial key: `biomarkers`, resulting key: `biomarkers`)
    - Diseases (initial key: `conditionQualifier_id`, resulting key: `conditionQualifier`)
    - Therapies (initial key: `therapies`, resulting key: `objectTherapeutic`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the proposition records.
    """

    def dereference_biomarkers(self, biomarkers: list[dict]) -> None:
        """
        Dereferences the `biomarkers` key in each proposition record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `biomarkers` key within each record. This key is expected to be present within each record, so a KeyError will
        be raised if it is missing.

        Args:
            biomarkers (list[dict]): list of dictionaries to dereference against.

        Raises:
            KeyError: If the referenced_key, `biomarkers`, is not found in a record.
        """
        self.dereference_list(
            referenced_key='biomarkers',
            referenced_records=biomarkers,
            key_always_present=True
        )

    def dereference_diseases(self, diseases: list[dict]) -> None:
        """
        Dereferences the `conditionQualifier_id` key in each proposition record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `conditionQualifier_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            diseases (list[dict]): list of dictionaries to dereference against.

        Raises:
            KeyError: If the referenced_key, `conditionQualifier_id`, is not found in a record.
        """
        self.dereference_single(
            referenced_key='conditionQualifier_id',
            referenced_records=diseases,
            new_key_name='conditionQualifier'
        )

    def dereference_therapies(self, therapies: list[dict]) -> None:
        """
        Dereferences the `therapies` key in each proposition record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `therapies` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            therapies (list[dict]): list of dictionaries to dereference against.

        Raises:
            KeyError: If the referenced_key, `therapies`, is not found in a record.
        """
        self.dereference_list(
            referenced_key='therapies',
            referenced_records=therapies,
            key_always_present=True
            # This will not be True once we re-expand beyond sensitive relationships
        )

class Statements(BaseTable):
    """
    Represents the Statements table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Contributions (key: `contributions`)
    - Documents (key: `reportedIn`)
    - Propositions (key: `proposition_id`)
    - Indications (key: `indications`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the statement records.
    """

    def dereference_contributions(self, contributions: list[dict]) -> None:
        """
        Dereferences the `contributions` key in each statement record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `contributions` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            contributions (list[dict]): list of dictionaries to dereference against.

        Raises:
            KeyError: If the referenced_key, `contributions`, is not found in a record.
        """
        self.dereference_list(
            referenced_key='contributions',
            referenced_records=contributions,
            key_always_present=True
        )

    def dereference_documents(self, documents: list[dict]) -> None:
        """
        Dereferences the `reportedIn` key in each statement record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `reportedIn` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            documents (list[dict]): list of dictionaries to dereference against.

        Raises:
            KeyError: If the referenced_key, `reportedIn`, is not found in a record.
        """
        self.dereference_list(
            referenced_key='reportedIn',
            referenced_records=documents,
            key_always_present=True
        )

    def dereference_propositions(self, propositions: list[dict]) -> None:
        """
        Dereferences the `proposition_id` key in each statement record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `proposition_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.

        Args:
            propositions (list[dict]): list of dictionaries to dereference against.

        Raises:
            KeyError: If the referenced_key, `proposition_id`, is not found in a record.
        """
        self.dereference_single(
            referenced_key='proposition_id',
            referenced_records=propositions,
            new_key_name='proposition'
        )

    def dereference_indications(self, indications: list[dict]) -> None:
        """
        Dereferences the `indication_id` key in each statement record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `indication_id` key within each record. This key is expected to be present within each record, so a
        KeyError will be raised if it is missing.
        Note: This will eventually not be expected to be present within each record, once we add more than regulatory approvals.

        Args:
            indications (list[dict]): list of dictionaries to dereference against.

        Raises:
            KeyError: If the referenced_key, `indication_id`, is not found in a record.
        """
        self.dereference_single(
            referenced_key='indication_id',
            referenced_records=indications,
            new_key_name='indication'
        )

class Therapies(BaseTable):
    """
    Represents the Therapies table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table does not currently reference any other tables.

    Attributes:
        records (list[dict]): A list of dictionaries representing the therapy records.
    """

    pass

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
    about = json_utils.load(file=input_paths['about'])
    agents = json_utils.load(file=input_paths['agents'])
    biomarkers = json_utils.load(file=input_paths['biomarkers'])
    contributions = json_utils.load(file=input_paths['contributions'])
    diseases = json_utils.load(file=input_paths['diseases'])
    documents = json_utils.load(file=input_paths['documents'])
    genes = json_utils.load(file=input_paths['genes'])
    indications = json_utils.load(file=input_paths['indications'])
    organizations = json_utils.load(file=input_paths['organizations'])
    propositions = json_utils.load(file=input_paths['propositions'])
    statements = json_utils.load(file=input_paths['statements'])
    therapies = json_utils.load(file=input_paths['therapies'])

    agents = Agents(records=agents)
    biomarkers = Biomarkers(records=biomarkers)
    contributions = Contributions(records=contributions)
    diseases = Diseases(records=diseases)
    documents = Documents(records=documents)
    genes = Genes(records=genes)
    indications = Indications(records=indications)
    organizations = Organizations(records=organizations)
    propositions = Propositions(records=propositions)
    statements = Statements(records=statements)
    therapies = Therapies(records=therapies)

    # biomarkers; references genes.json
    biomarkers.dereference_genes(genes=genes.records)

    # contributions; references agents.json
    contributions.dereference_agents(agents=agents.records)

    # documents; references organizations.json
    documents.dereference_organizations(organizations=organizations.records)

    # indications; references documents.json
    indications.dereference_documents(documents=documents.records)

    # propositions; references biomarkers.json, diseases.json, and therapies.json
    propositions.dereference_biomarkers(biomarkers=biomarkers.records)
    propositions.dereference_diseases(diseases=diseases.records)
    propositions.dereference_therapies(therapies=therapies.records)

    # statements; references contributions.json, documents.json, propositions.json, and indications.json
    statements.dereference_contributions(contributions=contributions.records)
    statements.dereference_documents(documents=documents.records)
    statements.dereference_propositions(propositions=propositions.records)
    statements.dereference_indications(indications=indications.records)

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
        '--output',
        help='Output json file',
        default='moalmanac-draft.dereferenced.json'
    )
    args = arg_parser.parse_args()

    input_data = {
        'about': args.about,
        'agents': args.agents,
        'biomarkers': args.biomarkers,
        'contributions': args.contributions,
        'diseases': args.diseases,
        'documents': args.documents,
        'genes': args.genes,
        'indications': args.indications,
        'organizations': args.organizations,
        'propositions': args.propositions,
        'statements': args.statements,
        'therapies': args.therapies
    }

    dereferenced = main(input_paths=input_data)
    json_utils.write_dict(
        data=dereferenced,
        keys_list=['content'],
        file=args.output
    )