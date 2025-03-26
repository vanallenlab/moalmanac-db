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

    # biomarkers; references genes.json
    dereferenced_biomarkers = Dereference.list(
        records=biomarkers,
        referenced_key='genes',
        referenced_records=genes,
        key_always_present=False
    )

    # contributions; references agents.json
    dereferenced_contributions = Dereference.integer(
        records=contributions,
        referenced_key='agent_id',
        referenced_records=agents,
        new_key_name='agent',
    )

    # documents; references organizations.json
    dereferenced_documents = Dereference.integer(
        records=documents,
        referenced_key='organization_id',
        referenced_records=organizations,
        new_key_name='organization'
    )

    # indications; references documents.json
    dereferenced_indications = Dereference.integer(
        records=indications,
        referenced_key='document_id',
        referenced_records=dereferenced_documents,
        new_key_name='document'
    )

    # propositions; references biomarkers.json, diseases.json, and therapies.json
    dereferenced_propositions = Dereference.list(
        records=propositions,
        referenced_key='biomarkers',
        referenced_records=dereferenced_biomarkers,
        key_always_present=True
    )
    dereferenced_propositions = Dereference.integer(
        records=dereferenced_propositions,
        referenced_key='conditionQualifier_id',
        referenced_records=diseases,
        new_key_name='conditionQualifier'
    )
    dereferenced_propositions = Dereference.list(
        records=dereferenced_propositions,
        referenced_key='therapies',
        referenced_records=therapies,
        key_always_present=True
        # This will not be True once we re-expand beyond sensitive relationships
    )

    # statements; references contributions.json, documents.json, and propositions.json
    dereferenced_statements = Dereference.list(
        records=statements,
        referenced_key='contributions',
        referenced_records=dereferenced_contributions,
        key_always_present=True
    )
    dereferenced_statements = Dereference.list(
        records=dereferenced_statements,
        referenced_key='reportedIn',
        referenced_records=dereferenced_documents,
        key_always_present=True
    )
    dereferenced_statements = Dereference.integer(
        records=dereferenced_statements,
        referenced_key='proposition_id',
        referenced_records=dereferenced_propositions,
        new_key_name='proposition'
    )
    dereferenced_statements = Dereference.integer(
        records=dereferenced_statements,
        referenced_key='indication_id',
        referenced_records=dereferenced_indications,
        new_key_name='indication'
    )

    return {
        'about': about,
        'content': dereferenced_statements
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