import argparse
import json
import typing


class Dereference:
    """
    Functions to dereference, depending on the field type to dereference
    """

    @staticmethod
    def fetch_records_by_key_value(records: list[dict], value: typing.Any, key: str = "id", warn: bool = True) -> list[dict]:
        """
        Retrieves records where a specific field matches a given value.

        Args:
            records (list[dict]): A list of dictionaries to search.
            value (any): The value to match.
            key (str): The field to check (default: "id").
            warn (bool): Whether to warn and exit if the number of results is not 1 (default: True).

        Returns:
            list[dict]: A list of matching records.

        Raises:
            ValueError: If the number of results is not exactly 1 and warnings are enabled.
        """
        results = [record for record in records if record.get(key) == value]

        if warn and len(results) != 1:
            ValueError(f"Warning: Expected 1 result for {key} == {value}, found {len(results)}.")

        return results

    @classmethod
    def integer(cls, records: list[dict], referenced_key: str, referenced_records: list[dict], new_key_name: str) -> list[dict]:
        """
        Dereferences a key for each record in records, where the key's value references a single record (i.e. is an integer).

        Args:
            records (list[dict]): list of dictionaries that require a key to be dereferenced.
            referenced_key (str): name of the key in `records` to dereference.
            referenced_records (str): list of dictionaries that the referenced_key refers to.
            new_key_name (str): key to store dereferenced record in `records`. this key replaces referenced_key.

        Raises:
            KeyError: If the referenced_key is not found in the record.
        """

        dereferenced_records = []
        for record in records:
            keys = list(record.keys())
            if not referenced_key in keys:
                raise KeyError(f"Key '{referenced_key}' not found in {record}.")

            referenced_record = cls.fetch_records_by_key_value(
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
        Dereferences a key for each record in records, presuming that the corresponding value is a list.

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
                _value = cls.fetch_records_by_key_value(
                    records=referenced_records,
                    key='id',
                    value=value
                )
                _values.append(_value[0])
            record[referenced_key] = _values
        return records


    @staticmethod
    def rename_key(dictionary: dict, old_key: str, new_key: str) -> None:
        """
        Renames a key in a dictionary.

        Args:
            dictionary (dict): The dictionary to modify.
            old_key (str): The key to rename.
            new_key (str): The new key name.

        Raises:
            KeyError: If the old_key does not exist in the dictionary.
            ValueError: If the new_key already exists in the dictionary.
        """
        if old_key not in dictionary:
            raise KeyError(f"Key '{old_key}' not found in the dictionary.")

        if new_key in dictionary:
            raise ValueError(f"Key '{new_key}' already exists in the dictionary.")

        dictionary[new_key] = dictionary.pop(old_key)


def load_json(file: str) -> list[dict]:
    """
    Loads and parses a JSON file.

    Args:
        file (str): Path to the JSON file.

    Returns:
        list[dict]: Parsed data from the JSON file.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    try:
        with open(file, "r") as fp:
            data = json.load(fp)
        return data
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {file}") from e
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in file: {file}", e.doc, e.pos)


def write_json_dict(data: dict, keys_list: list[str], file:str) -> None:
    """
    Write json from input object of dictionary

    Args:
        data (dict): A object of type dictionary, though one key value should be a list of dictionaries (records)
        keys_list (list[str]): A list of keys that are of type list[dict] (records).
        file (str): The output file path

    Raises:
        TypeError: If the keys provided with keys_list are not a list of dictionaries.
        ValueError: If the JSON serialization fails.
    """

    if not isinstance(data, dict):
        raise TypeError("The input data must be of type dict")

    for key in keys_list:
        if not all(isinstance(item, dict) for item in data[key]):
            raise TypeError(f"All elements in the list must be dictionaries for key {key}.")

    try:
        # Serialize python object (data) to a JSON formatted string
        json_object = json.dumps(data, indent=4)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize the object to JSON: {e}")

    try:
        # Write json string to the specified file
        with open(file, "w") as outfile:
            outfile.write(json_object)
        print(f"JSON successfully written to {file}")
    except IOError as e:
        raise IOError(f"Failed to write to file {file}: {e}")


def write_json_records(data: list[dict], file:str) -> None:
    """
    Writes json from input object of list[dict]

    Args:
        data (list[dict]): A object of type list with elements as dictionaries
        file (str): The output file path

    Raises:
        TypeError: If the input is not a list of dictionaries.
        ValueError: If the JSON serialization fails.
    """
    if not isinstance(data, list):
        raise TypeError("The input data must be of type list")

    if not all(isinstance(item, dict) for item in data):
        raise TypeError("All elements in the list must be dictionaries.")

    try:
        # Serialize python object (data) to a JSON formatted string
        json_object = json.dumps(data, indent=4)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize the object to JSON: {e}")

    try:
        # Write json string to the specified file
        with open(file, "w") as outfile:
            outfile.write(json_object)
        print(f"JSON successfully written to {file}")
    except IOError as e:
        raise IOError(f"Failed to write to file {file}: {e}")


def main(input_paths, output):
    about = load_json(file=input_paths['about'])
    agents = load_json(file=input_paths['agents'])
    biomarkers = load_json(file=input_paths['biomarkers'])
    contributions = load_json(file=input_paths['contributions'])
    diseases = load_json(file=input_paths['diseases'])
    documents = load_json(file=input_paths['documents'])
    genes = load_json(file=input_paths['genes'])
    indications = load_json(file=input_paths['indications'])
    organizations = load_json(file=input_paths['organizations'])
    propositions = load_json(file=input_paths['propositions'])
    statements = load_json(file=input_paths['statements'])
    therapies = load_json(file=input_paths['therapies'])

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

    # propositions; references biomarkers.json, diseases.json, indications.json, and therapies.json
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
    dereferenced_propositions = Dereference.integer(
        records=dereferenced_propositions,
        referenced_key='indication_id',
        referenced_records=dereferenced_indications,
        new_key_name='indication'
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

    # Create final object
    dereferenced = {
        'about': about,
        'content': dereferenced_statements
    }

    # Write
    write_json_dict(
        data=dereferenced,
        keys_list=['content'],
        file=output
    )


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

    main(input_paths=input_data, output=args.output)
