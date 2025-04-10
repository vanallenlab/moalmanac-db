import argparse

import json_utils # Local import


class Dereference:
    """
    Functions to dereference, depending on the field type to dereference
    """

    @classmethod
    def integer(cls, records: list[dict], referenced_key: str, referenced_records: list[dict], new_key_name: str) -> list[dict]:
        """
        Dereferences a key for each record in records, where the key's value references a single record (i.e. is an integer).

        Args:
            records (list[dict]): list of dictionaries that require a key to be dereferenced.
            referenced_key (str): name of the key in `records` to dereference.
            referenced_records (list[dict]): list of dictionaries that the referenced_key refers to.
            new_key_name (str): key to store dereferenced record in `records`. this key replaces `referenced_key`.

        Raises:
            KeyError: If the referenced_key is not found in the record.
        """

        dereferenced_records = []
        for record in records:
            keys = list(record.keys())
            if not referenced_key in keys:
                raise KeyError(f"Key '{referenced_key}' not found in {record}.")

            referenced_record = json_utils.fetch_records_by_key_value(
                records=referenced_records,
                key='id',
                value=record[referenced_key]
            )
            referenced_record = referenced_record[0]

            new_record = {}
            for key, value in record.items():
                if key == referenced_key:
                    new_record[new_key_name] = referenced_record
                else:
                    new_record[key] = value

            dereferenced_records.append(new_record)
        return dereferenced_records

    @classmethod
    def list(cls, records: list[dict], referenced_key: str, referenced_records: list[dict], key_always_present: bool = True) -> list[dict]:
        """
        Dereferences a key for each record in records, where the key's value can store multiple records (i.e. is a list).

        Args:
            records (list[dict]): list of dictionaries that require a key to be dereferenced.
            referenced_key (str): name of the key in records to dereference.
            referenced_records (str): list of dictionaries that the referenced_key refers to.
            key_always_present (bool): If True, the referenced_key is present in all records.

        Raises:
            KeyError: If the referenced_key is not found in the record, despite key_always_present being True.
        """

        for record in records:
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
                _values.append(_value[0])
            record[referenced_key] = _values
        return records


class BaseTable:
    def __init__(self, records: list[dict]):
        self.records = records

    def dereference_integer(self, referenced_key: str, referenced_records: list[dict], new_key_name: str) -> list[dict]:
        return Dereference.integer(
            records=self.records,
            referenced_key=referenced_key,
            referenced_records=referenced_records,
            new_key_name=new_key_name
        )

    def dereference_list(self, referenced_key: str, referenced_records: list[dict], key_always_present: bool = True) -> list[dict]:
        return Dereference.list(
            records=self.records,
            referenced_key=referenced_key,
            referenced_records=referenced_records,
            key_always_present=key_always_present
        )


class Agents(BaseTable):
    """
    Dereferences the Agents table. It inherits common functionality from the BaseTable class and dereferences
    fields that reference other tables. This table does not currently reference any other tables.

    Attributes:
        records (list[dict]): A list of dictionaries representing the agent records.
    """

    pass

class Biomarkers(BaseTable):
    """
    Dereferences the Biomarkers table. It inherits common functionality from the BaseTable class and dereferences
    fields that reference other tables. This table references the following tables:
    - Genes (field: 'organization_id')

    Attributes:
        records (list[dict]): A list of dictionaries representing the document records.
    """

    def dereference_genes(self, genes):
        self.records = self.dereference_list(
            referenced_key='genes',
            referenced_records=genes,
            key_always_present=False
        )

class Contributions(BaseTable):
    """
    Dereferences the Contributions table. It inherits common functionality from the BaseTable class and dereferences
    fields that reference other tables. This table references the following tables:
    - Agents (field: 'agent_id')

    Attributes:
        records (list[dict]): A list of dictionaries representing the contribution records.
    """

    def dereference_agents(self, agents):
        self.records = self.dereference_integer(
            referenced_key='agent_id',
            referenced_records=agents,
            new_key_name='agent'
        )

class Diseases(BaseTable):
    """
    Dereferences the Diseases table. It inherits common functionality from the BaseTable class and dereferences
    fields that reference other tables. This table does not currently reference any other tables.

    Attributes:
        records (list[dict]): A list of dictionaries representing the disease records.
    """

    pass

class Documents(BaseTable):
    """
    Dereferences the Documents table. It inherits common functionality from the BaseTable class and dereferences
    fields that reference other tables. This table references the following tables:
    - Organizations (field: 'organization_id')

    Attributes:
        records (list[dict]): A list of dictionaries representing the document records.
    """

    def dereference_organizations(self, organizations):
        """
        Dereferences the organization field in the Documents table and replaces 'organization_id' field with 'organization'.

        Args:
            organizations (list[dict]): A list of dictionaries representing the organization records.

        Raises:
            KeyError: If the referenced key, 'organization_id', is not found within a document record.
        """

        self.records = self.dereference_integer(
            referenced_key='organization_id',
            referenced_records=organizations,
            new_key_name='organization'
        )

class Genes(BaseTable):
    """
    Dereferences the Genes table. It inherits common functionality from the BaseTable class and dereferences
    fields that reference other tables. This table does not currently reference any other tables.

    Attributes:
        records (list[dict]): A list of dictionaries representing the gene records.
    """

    pass

class Indications(BaseTable):
    """
    Dereferences the Indications table. It inherits common functionality from the BaseTable class and dereferences
    fields that reference other tables. This table references the following tables:
    - Documents (field: 'document_id')

    Attributes:
        records (list[dict]): A list of dictionaries representing the indication records.
    """

    def dereference_documents(self, documents):
        self.records = self.dereference_integer(
            referenced_key='document_id',
            referenced_records=documents,
            new_key_name='document'
        )

class Organizations(BaseTable):
    """
    Dereferences the Organizations table. It inherits common functionality from the BaseTable class and dereferences
    fields that reference other tables. This table does not currently reference any other tables.

    Attributes:
        records (list[dict]): A list of dictionaries representing the organization records.
    """

    pass

class Propositions(BaseTable):
    """
    Dereferences the Propositions table. It inherits common functionality from the BaseTable class and dereferences
    fields that reference other tables. This table references the following tables:
    - Biomarkers (field: 'biomarkers')
    - Diseases (field: 'conditionQualifier_id')
    - Therapies (field: 'therapies')

    Attributes:
        records (list[dict]): A list of dictionaries representing the proposition records.
    """

    def dereference_biomarkers(self, biomarkers):
        self.records = self.dereference_list(
            referenced_key='biomarkers',
            referenced_records=biomarkers,
            key_always_present=False
        )

    def dereference_diseases(self, diseases):
        self.records = self.dereference_integer(
            referenced_key='conditionQualifier_id',
            referenced_records=diseases,
            new_key_name='conditionQualifier'
        )

    def dereference_therapies(self, therapies):
        self.records = self.dereference_list(
            referenced_key='therapies',
            referenced_records=therapies,
            key_always_present=True
            # This will not be True once we re-expand beyond sensitive relationships
        )

class Statements(BaseTable):
    """
    Dereferences the Statements table. It inherits common functionality from the BaseTable class and dereferences
    fields that reference other tables. This table references the following tables:
    - Contributions (field: 'contributions')
    - Documents (field: 'reportedIn')
    - Propositions (field: 'proposition_id')
    - Indications (field: 'indications')

    Attributes:
        records (list[dict]): A list of dictionaries representing the statement records.
    """

    def dereference_contributions(self, contributions):
        self.records = self.dereference_list(
            referenced_key='contributions',
            referenced_records=contributions,
            key_always_present=True
        )

    def dereference_documents(self, documents):
        self.records = self.dereference_list(
            referenced_key='reportedIn',
            referenced_records=documents,
            key_always_present=True
        )

    def dereference_propositions(self, propositions):
        self.records = self.dereference_integer(
            referenced_key='proposition_id',
            referenced_records=propositions,
            new_key_name='proposition'
        )

    def dereference_indications(self, indications):
        self.records = self.dereference_integer(
            referenced_key='indication_id',
            referenced_records=indications,
            new_key_name='indication'
        )

class Therapies(BaseTable):
    """
    Dereferences the Therapies table. It inherits common functionality from the BaseTable class and dereferences
    fields that reference other tables. This table does not currently reference any other tables.

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