# Postpones evaluation of type annotations so classes can be referenced before they are defined
# (avoids needing quotes around type names)
from __future__ import annotations

import argparse
import dataclasses
import os
import pathlib
import typing

# Local imports
from utils import json_utils
from utils import read
from utils import write


@dataclasses.dataclass
class FKSingle:
    """
    Descriptor for a foreign key that references a single record in another table.

    Attributes:
        src_key (str): The key in the record whose value is the foreign key.
        dest_key (str): The key name written after dereferencing (replaces src_key).
        get_table (typing.Callable[[Database], BaseTable]): Returns the referenced table from the Database.
        post (typing.Callable[[dict], dict] | None): Optional function applied to the resolved record.
    """

    src_key: str
    dest_key: str
    get_table: typing.Callable[[Database], BaseTable]
    post: typing.Callable[[dict], dict] | None = None


@dataclasses.dataclass
class FKList:
    """
    Descriptor for a foreign key that references a list of records in another table.

    Attributes:
        src_key (str): The key in the record whose value is a list of foreign keys.
        dest_key (str): The key name written after dereferencing. Pass src_key if unchanged.
        get_table (typing.Callable[[Database], BaseTable]): Returns the referenced table from the Database.
        key_always_present (bool): If True, raise KeyError when src_key is absent from a record.
        post (typing.Callable[[dict], object] | None): Optional function applied to each resolved record.
    """

    src_key: str
    dest_key: str
    get_table: typing.Callable[[Database], BaseTable]
    key_always_present: bool = True
    post: typing.Callable[[dict], object] | None = None


def strip_keys(*keys: str) -> typing.Callable[[dict], dict]:
    """
    Returns a function that removes the specified keys from a record dict.

    Args:
        *keys (str): Key names to exclude from the record.

    Returns:
        typing.Callable[[dict], dict]: A function that accepts a record and returns a copy with the specified keys removed.
    """
    return lambda record: {k: v for k, v in record.items() if k not in keys}


def extract_url_value(url: dict) -> str:
    """
    Extracts the URL string from a resolved URL record.

    Args:
        url (dict): A resolved URL record containing a `url` key.

    Returns:
        str: The URL string.
    """
    return url["url"]


class BaseTable:
    """
    A base class for managing and dereferencing records across database tables. This class provides common
    functionality for dereferencing keys that reference other tables. It serves as a template for specific table
    classes, which inherit from BaseTable and implement additional table-specific logic.

    Attributes:
        records (list[dict]): list of dictionaries that represent one table within the relational database.
        foreign_keys (list): Class-level list of FKSingle or FKList descriptors declaring this table's
            foreign key relationships. Subclasses override this at the class level to declare their relationships.
    """

    foreign_keys: list = []

    def __init__(self, records: list[dict]):
        """
        Initializes the BaseTable with a list of records.

        Args:
            records (list[dict]): list of dictionaries that represent one table within the relational database.
        """
        self.records = records
        self._resolved = False

    def dereference(self, db: Database) -> None:
        """
        Dereferences all records in this table by resolving each declared foreign key.

        Iterates over `foreign_keys`, resolves each referenced table, then replaces each foreign key value
        in every record with the full referenced record. Each table is resolved at most once; subsequent
        calls are no-ops.

        Args:
            db (Database): An instance of the Database class containing all tables.
        """
        if self._resolved:
            return
        self._resolved = True
        for fk in self.foreign_keys:
            table = fk.get_table(db)
            table.dereference(db)
            for record in self.records:
                if isinstance(fk, FKSingle):
                    self.dereference_single(record, fk.src_key, table.records)
                    self.replace_key(record, fk.src_key, fk.dest_key)
                    if fk.post is not None:
                        record[fk.dest_key] = fk.post(dict(record[fk.dest_key]))
                else:
                    self.dereference_list(
                        record, fk.src_key, table.records, fk.key_always_present
                    )
                    if fk.post is not None and fk.src_key in record:
                        record[fk.src_key] = [
                            fk.post(item) for item in record[fk.src_key]
                        ]
                    if fk.src_key != fk.dest_key:
                        self.replace_key(record, fk.src_key, fk.dest_key)

    @staticmethod
    def dereference_single(
        record: dict, referenced_key: str, referenced_records: list[dict]
    ) -> None:
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

        referenced_record = json_utils.get_record_by_key_value(
            records=referenced_records,
            key="id",
            value=record[referenced_key],
            strict=True,
        )

        record[referenced_key] = referenced_record

    @staticmethod
    def dereference_list(
        record: dict,
        referenced_key: str,
        referenced_records: list[dict],
        key_always_present: bool = True,
    ) -> None:
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
            raise KeyError(
                f"Key '{referenced_key}' not found but should be found in {record}"
            )

        if referenced_key not in record:
            pass
        else:
            _values = []
            for value in record[referenced_key]:
                _value = json_utils.get_record_by_key_value(
                    records=referenced_records, key="id", value=value
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

    def write_records(self, output_dir: str, quiet: bool = False) -> None:
        """
        Writes each record in this table to its own JSON file in the given directory.

        Each file is named `{record['id']}.json`.

        Args:
            output_dir (str): Directory path to write the individual record files into.
            quiet (bool): Suppress print statements if True.
        """
        for record in self.records:
            filename = f"{record['id']}.json"
            path = os.path.join(output_dir, filename)
            write.dictionary(data=record, keys_list=[], file=path, quiet=quiet)


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

    foreign_keys = [
        FKList("genes", "genes", lambda db: db.genes, key_always_present=False),
    ]


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
    - Agents (initial key: `agent_id`, resulting key: `contributor`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the contribution records.
    """

    foreign_keys = [
        FKSingle(
            "agent_id",
            "contributor",
            lambda db: db.agents,
            post=strip_keys("extensions"),
        ),
    ]


class Diseases(BaseTable):
    """
    Represents the Diseases table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Codings (initial key: `primary_coding_id`, resulting_key: `primaryCoding`)
    - Mappings (initial key: `mappings`, resulting_key: `mappings`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the therapy records.
    """

    foreign_keys = [
        FKSingle("primary_coding_id", "primaryCoding", lambda db: db.codings),
        FKList(
            "mappings",
            "mappings",
            lambda db: db.mappings,
            post=strip_keys("id", "primary_coding_id"),
        ),
    ]


class Documents(BaseTable):
    """
    Represents the Documents table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Agents (initial key: `agent_id`, resulting key: `agent`)
    - URLs (initial key: `urls`, resulting key: `urls`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the document records.
    """

    foreign_keys = [
        FKSingle(
            "agent_id", "agent", lambda db: db.agents, post=strip_keys("extensions")
        ),
        FKList("urls", "urls", lambda db: db.urls, post=extract_url_value),
    ]

    def convert_fields_to_extensions(self):
        """
        Converts relevant keys to extensions.
        """
        extension_fields = [
            "agent",
            "company",
            "drug_name_brand",
            "drug_name_generic",
            "first_publication_date",
            "identification_number",
            "publication_date",
            "status",
        ]
        for record in self.records:
            extensions = [
                {
                    "name": "agent",
                    "value": record["agent"],
                    "description": "The organization that published this document.",
                },
                {
                    "name": "company",
                    "value": record["company"],
                    "description": "The company that manufactures the cancer drug. Only applicable to market authorization documents.",
                },
                {
                    "name": "drug_name_brand",
                    "value": record["drug_name_brand"],
                    "description": "The brand name of the cancer drug, per this document. Only applicable to market authorization documents.",
                },
                {
                    "name": "drug_name_generic",
                    "value": record["drug_name_generic"],
                    "description": "The generic name of the cancer drug, per this document. Only applicable to market authorization documents.",
                },
                {
                    "name": "first_publication_date",
                    "value": record["first_publication_date"],
                    "description": "The publication date for the initial version of this document.",
                },
                {
                    "name": "identification_number",
                    "value": record["identification_number"],
                    "description": "Identification number used by the publishing organization.",
                },
                {
                    "name": "publication_date",
                    "value": record["publication_date"],
                    "description": "The publication date for the document.",
                },
                {
                    "name": "status",
                    "value": record["status"],
                    "description": "Whether this document is Active or Deprecated within moalmanac-db.",
                },
            ]
            record["extensions"] = extensions
            for field in extension_fields:
                self.remove_key(record=record, key=field)

    def dereference(self, db: Database) -> None:
        """
        Dereferences all referenced keys within the Documents table, then converts fields to extensions.

        Resolves foreign keys declared in `foreign_keys` via the base class, then applies
        `convert_fields_to_extensions`. Each table is resolved at most once; subsequent calls are no-ops.

        Args:
            db (Database): An instance of the Database class containing all tables.
        """
        if self._resolved:
            return
        super().dereference(db)
        self.convert_fields_to_extensions()


class Genes(BaseTable):
    """
    Represents the Genes table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Codings (initial key: `primary_coding_id`, resulting_key: `primaryCoding`)
    - Mappings (initial key: `mappings`, resulting_key: `mappings`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the therapy records.
    """

    foreign_keys = [
        FKSingle("primary_coding_id", "primaryCoding", lambda db: db.codings),
        FKList(
            "mappings",
            "mappings",
            lambda db: db.mappings,
            post=strip_keys("id", "primary_coding_id"),
        ),
    ]


class Indications(BaseTable):
    """
    Represents the Indications table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Documents (initial key: `document_id`, resulting key: `document`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the indication records.
    """

    foreign_keys = [
        FKSingle("document_id", "document", lambda db: db.documents),
    ]


class Mappings(BaseTable):
    """
    Represents the Mappings table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Codings (initial key: `coding_id`, resulting key: `coding`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the contribution records.
    """

    foreign_keys = [
        FKSingle("coding_id", "coding", lambda db: db.codings),
    ]


class Propositions(BaseTable):
    """
    Represents the Propositions table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Biomarkers (initial key: `biomarkers`, resulting key: `biomarkers`)
    - Diseases (initial key: `conditionQualifier_id`, resulting key: `conditionQualifier`)
    - Therapies (initial key: `therapy_id`, resulting key: `objectTherapeutic`)
    - TherapyGroups (initial_key: `therapy_group_id`, resulting key: `objectTherapeutic`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the proposition records.
    """

    foreign_keys = [
        FKSingle("conditionQualifier_id", "conditionQualifier", lambda db: db.diseases),
        FKList("biomarkers", "biomarkers", lambda db: db.biomarkers),
    ]

    def dereference(self, db: Database) -> None:
        """
        Dereferences all referenced keys within the Propositions table.

        Resolves therapies and therapy groups before delegating FK resolution to the base class,
        then applies the custom therapeutics dereferencing. Each table is resolved at most once;
        subsequent calls are no-ops.

        Args:
            db (Database): An instance of the Database class containing all tables.
        """
        if self._resolved:
            return
        db.therapies.dereference(db)
        db.therapy_groups.dereference(db)

        # Maybe change this to just do therapy groups?

        super().dereference(db)
        self.dereference_therapeutics(
            therapies=db.therapies, therapy_groups=db.therapy_groups
        )

    def dereference_therapeutics(
        self, therapies: Therapies, therapy_groups: TherapyGroups
    ) -> None:
        """
        Dereferences the `therapy_id` key or `therapy_group_id` key in each proposition record.

        Utilizes the `dereference_list` function from the BaseTable class to replace the value associated with the
        `objectTherapeutic` key within each record.

        Args:
            therapies (Therapies): list of dictionaries to dereference `therapy_ids` against.
            therapy_groups (TherapyGroups): list of dictionaries to dereference `therapy_group_ids` against.

        Raises:
            KeyError: If neither referenced_key values, `therapy_id` or `therapy_group_id, are not found in a record.
        """
        for record in self.records:
            if isinstance(record["therapy_id"], int):
                self.dereference_single(
                    record=record,
                    referenced_key="therapy_id",
                    referenced_records=therapies.records,
                )
                self.replace_key(
                    record=record,
                    old_key="therapy_id",
                    new_key="objectTherapeutic",
                )
                self.remove_key(record=record, key="therapy_group_id")
            elif isinstance(record["therapy_group_id"], int):
                self.dereference_single(
                    record=record,
                    referenced_key="therapy_group_id",
                    referenced_records=therapy_groups.records,
                )
                self.replace_key(
                    record=record,
                    old_key="therapy_group_id",
                    new_key="objectTherapeutic",
                )
                self.remove_key(record=record, key="therapy_id")
            else:
                raise KeyError(
                    f"Neither 'therapy_id' nor 'therapy_group_id' are keys found in {record}"
                )


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

    foreign_keys = [
        FKList("contributions", "contributions", lambda db: db.contributions),
        FKList("reportedIn", "reportedIn", lambda db: db.documents),
        FKSingle("indication_id", "indication", lambda db: db.indications),
        FKSingle("proposition_id", "proposition", lambda db: db.propositions),
        FKSingle("strength_id", "strength", lambda db: db.strengths),
    ]

    def dereference(self, db: Database) -> None:
        """
        Dereferences all referenced keys within the Statements table.

        Resolves foreign keys declared in `foreign_keys` via the base class, then copies the indication
        description onto each statement record. Each table is resolved at most once; subsequent calls are
        no-ops.

        Args:
            db (Database): An instance of the Database class containing all tables.
        """
        if self._resolved:
            return
        super().dereference(db)
        for record in self.records:
            indication = record.get("indication")
            if isinstance(indication, dict):
                description = indication.get("description")
                if description is not None:
                    record["description"] = description


class Strengths(BaseTable):
    """
    Represents the Strengths table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Codings (initial key: `primary_coding_id`, resulting_key: `primaryCoding`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the therapy records.
    """

    foreign_keys = [
        FKSingle("primary_coding_id", "primaryCoding", lambda db: db.codings),
    ]


class Therapies(BaseTable):
    """
    Represents the Therapies table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Codings (initial key: `primary_coding_id`, resulting_key: `primaryCoding`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the therapy records.
    """

    foreign_keys = [
        FKSingle("primary_coding_id", "primaryCoding", lambda db: db.codings),
        FKList(
            "mappings",
            "mappings",
            lambda db: db.mappings,
            post=strip_keys("id", "primary_coding_id"),
        ),
    ]


class TherapyGroups(BaseTable):
    """
    Represents the Therapy Groups table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Therapies (key: `therapies`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the therapy records.
    """

    foreign_keys = [
        FKList("therapies", "therapies", lambda db: db.therapies),
    ]


class URLs(BaseTable):
    """
    Represents the URLs table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table does not currently reference any other tables.

    Attributes:
        records (list[dict]): A list of dictionaries representing the url records.
    """

    pass


@dataclasses.dataclass
class Database:
    """
    A container holding all table instances for the relational database.

    Attributes:
        agents (Agents): An instance of the Agents class.
        biomarkers (Biomarkers): An instance of the Biomarkers class.
        codings (Codings): An instance of the Codings class.
        contributions (Contributions): An instance of the Contributions class.
        diseases (Diseases): An instance of the Diseases class.
        documents (Documents): An instance of the Documents class.
        genes (Genes): An instance of the Genes class.
        indications (Indications): An instance of the Indications class.
        mappings (Mappings): An instance of the Mappings class.
        propositions (Propositions): An instance of the Propositions class.
        statements (Statements): An instance of the Statements class.
        strengths (Strengths): An instance of the Strengths class.
        therapies (Therapies): An instance of the Therapies class.
        therapy_groups (TherapyGroups): An instance of the TherapyGroups class.
        urls (URLs): An instance of the URLs class.
    """

    agents: Agents
    biomarkers: Biomarkers
    codings: Codings
    contributions: Contributions
    diseases: Diseases
    documents: Documents
    genes: Genes
    indications: Indications
    mappings: Mappings
    propositions: Propositions
    statements: Statements
    strengths: Strengths
    therapies: Therapies
    therapy_groups: TherapyGroups
    urls: URLs


def populate_statement_description(statements: list[dict], indications: list[dict]):
    """
    Populates the description field for statements from the description field from the associated indication.

    Args:
        indications (list[dict]): List of dictionaries of database indications.
        statements (list[dict]): List of dictionaries of database statements.

    Returns:
        list[dict]: List of dictionaries of database statements, with description value copied from indications for statements associated with an indication.
    """
    for statement in statements:
        indication_id = statement.get("indication_id", None)
        if indication_id:
            indication_record = json_utils.get_record_by_key_value(
                records=indications, key="id", value=indication_id
            )
            if indication_record:
                statement["description"] = indication_record["description"]
    write.records(data=statements, file=os.path.join("referenced", "statements.json"))
    return statements


def clear_output_dir(output_dir: str, quiet: bool = False) -> None:
    """
    Removes all JSON files from the given output directory.

    Args:
        output_dir (str): Path to the directory to clear.
        quiet (bool): Suppress print statements if True.
    """
    folder = pathlib.Path(output_dir)
    for json_file in folder.rglob("*.json"):
        json_file.unlink()
    if not quiet:
        print(f"Cleared {output_dir}")


_CONCEPT_DIRS = [
    ("agents", os.path.join("dereferenced", "agents")),
    ("biomarkers", os.path.join("dereferenced", "biomarkers")),
    ("codings", os.path.join("dereferenced", "codings")),
    ("contributions", os.path.join("dereferenced", "contributions")),
    ("diseases", os.path.join("dereferenced", "diseases")),
    ("documents", os.path.join("dereferenced", "documents")),
    ("genes", os.path.join("dereferenced", "genes")),
    ("indications", os.path.join("dereferenced", "indications")),
    ("mappings", os.path.join("dereferenced", "mappings")),
    ("propositions", os.path.join("dereferenced", "propositions")),
    ("statements", os.path.join("dereferenced", "statements")),
    ("strengths", os.path.join("dereferenced", "strengths")),
    ("therapies", os.path.join("dereferenced", "therapies")),
    ("therapy_groups", os.path.join("dereferenced", "therapy_groups")),
]


def write_all_concepts(
    input_paths: dict, clear: bool = False, quiet: bool = False
) -> None:
    """
    Writes per-concept JSON files for all 14 entity types to their output directories.

    Constructs a fresh Database from the raw input files (independent of any already-resolved
    full-DB tables), dereferences each entity, and writes one JSON file per record to
    `dereferenced/<entity>/<id>.json`.

    Args:
        input_paths (dict): Dictionary of paths to referenced JSON files.
        clear (bool): If True, remove existing JSON files from each output directory first.
        quiet (bool): Suppress print statements if True.
    """
    if clear:
        for _, output_dir in _CONCEPT_DIRS:
            clear_output_dir(output_dir, quiet=quiet)

    db = Database(
        agents=Agents(records=read.json_records(file=input_paths["agents"])),
        biomarkers=Biomarkers(
            records=read.json_records(file=input_paths["biomarkers"])
        ),
        codings=Codings(records=read.json_records(file=input_paths["codings"])),
        contributions=Contributions(
            records=read.json_records(file=input_paths["contributions"])
        ),
        diseases=Diseases(records=read.json_records(file=input_paths["diseases"])),
        documents=Documents(records=read.json_records(file=input_paths["documents"])),
        genes=Genes(records=read.json_records(file=input_paths["genes"])),
        indications=Indications(
            records=read.json_records(file=input_paths["indications"])
        ),
        mappings=Mappings(records=read.json_records(file=input_paths["mappings"])),
        propositions=Propositions(
            records=read.json_records(file=input_paths["propositions"])
        ),
        statements=Statements(
            records=read.json_records(file=input_paths["statements"])
        ),
        strengths=Strengths(records=read.json_records(file=input_paths["strengths"])),
        therapies=Therapies(records=read.json_records(file=input_paths["therapies"])),
        therapy_groups=TherapyGroups(
            records=read.json_records(file=input_paths["therapy_groups"])
        ),
        urls=URLs(records=read.json_records(file=input_paths["urls"])),
    )

    for attr, output_dir in _CONCEPT_DIRS:
        table = getattr(db, attr)
        table.dereference(db)
        table.write_records(output_dir, quiet=quiet)


def main(input_paths):
    """
    Creates a single JSON file for the Molecular Oncology Almanac (moalmanac) database by dereferencing
    referenced JSON files. By default, these are located in the referenced/ folder of this repository.

    Args:
        input_paths (dict): Dictionary of paths to referenced JSON files.

    Returns:
        dict: Dereferenced database, with keys:
            - about (dict): Dictionary containing database metadata, from referenced/about.json.
            - content (list[dict]): List of dictionaries containing the dereferenced database.
    """

    # Step 1: Read JSON files
    about = read.json_records(file=input_paths["about"])
    agents = read.json_records(file=input_paths["agents"])
    biomarkers = read.json_records(file=input_paths["biomarkers"])
    codings = read.json_records(file=input_paths["codings"])
    contributions = read.json_records(file=input_paths["contributions"])
    diseases = read.json_records(file=input_paths["diseases"])
    documents = read.json_records(file=input_paths["documents"])
    genes = read.json_records(file=input_paths["genes"])
    indications = read.json_records(file=input_paths["indications"])
    mappings = read.json_records(file=input_paths["mappings"])
    propositions = read.json_records(file=input_paths["propositions"])
    statements = read.json_records(file=input_paths["statements"])
    strengths = read.json_records(file=input_paths["strengths"])
    therapies = read.json_records(file=input_paths["therapies"])
    therapy_groups = read.json_records(file=input_paths["therapy_groups"])
    urls = read.json_records(file=input_paths["urls"])

    statements = populate_statement_description(
        indications=indications,
        statements=statements,
    )

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
    propositions = Propositions(records=propositions)
    statements = Statements(records=statements)
    strengths = Strengths(records=strengths)
    therapies = Therapies(records=therapies)
    therapy_groups = TherapyGroups(records=therapy_groups)
    urls = URLs(records=urls)

    # Step 3: Dereference the database and generate statements
    db = Database(
        agents=agents,
        biomarkers=biomarkers,
        codings=codings,
        contributions=contributions,
        diseases=diseases,
        documents=documents,
        genes=genes,
        indications=indications,
        mappings=mappings,
        propositions=propositions,
        statements=statements,
        strengths=strengths,
        therapies=therapies,
        therapy_groups=therapy_groups,
        urls=urls,
    )
    statements.dereference(db)

    data = {"about": about, "content": statements.records}
    write.dictionary(data=data, keys_list=["content"], file=args.output)
    return data


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog="dereference",
        description="dereferences moalmanac db (currently in draft and development).",
    )
    arg_parser.add_argument(
        "--about",
        help="json detailing db metadata",
        default=os.path.join("referenced", "about.json"),
    )
    arg_parser.add_argument(
        "--agents",
        help="json detailing agents",
        default=os.path.join("referenced", "agents.json"),
    )
    arg_parser.add_argument(
        "--biomarkers",
        help="json detailing db biomarkers",
        default=os.path.join("referenced", "biomarkers.json"),
    )
    arg_parser.add_argument(
        "--codings",
        help="json detailing db codings",
        default=os.path.join("referenced", "codings.json"),
    )
    arg_parser.add_argument(
        "--contributions",
        help="json detailing db contributions",
        default=os.path.join("referenced", "contributions.json"),
    )
    arg_parser.add_argument(
        "--diseases",
        help="json detailing db diseases",
        default=os.path.join("referenced", "diseases.json"),
    )
    arg_parser.add_argument(
        "--documents",
        help="json detailing db documents",
        default=os.path.join("referenced", "documents.json"),
    )
    arg_parser.add_argument(
        "--genes",
        help="json detailing db genes",
        default=os.path.join("referenced", "genes.json"),
    )
    arg_parser.add_argument(
        "--indications",
        help="json detailing db indications",
        default=os.path.join("referenced", "indications.json"),
    )
    arg_parser.add_argument(
        "--mappings",
        help="json detailing db mappings",
        default=os.path.join("referenced", "mappings.json"),
    )
    arg_parser.add_argument(
        "--propositions",
        help="json detailing db propositions",
        default=os.path.join("referenced", "propositions.json"),
    )
    arg_parser.add_argument(
        "--statements",
        help="json detailing db statements",
        default=os.path.join("referenced", "statements.json"),
    )
    arg_parser.add_argument(
        "--strengths",
        help="json detailing db strengths",
        default=os.path.join("referenced", "strengths.json"),
    )
    arg_parser.add_argument(
        "--therapies",
        help="json detailing db therapies",
        default=os.path.join("referenced", "therapies.json"),
    )
    arg_parser.add_argument(
        "--therapy-groups",
        help="json detailing db therapy groups",
        default=os.path.join("referenced", "therapy_groups.json"),
    )
    arg_parser.add_argument(
        "--urls",
        help="json detailing db urls",
        default=os.path.join("referenced", "urls.json"),
    )
    arg_parser.add_argument(
        "--output",
        help="Output json file",
        default="moalmanac-draft.dereferenced.json",
    )
    arg_parser.add_argument(
        "--write-concepts",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Write per-concept JSON files to dereferenced/<entity>/. Use --no-write-concepts to skip.",
    )
    arg_parser.add_argument(
        "--clear",
        action="store_true",
        help="Remove existing JSON files from all concept output directories before writing.",
    )
    arg_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress print messages when writing individual entities",
    )
    args = arg_parser.parse_args()

    input_data = {
        "about": args.about,
        "agents": args.agents,
        "biomarkers": args.biomarkers,
        "codings": args.codings,
        "contributions": args.contributions,
        "diseases": args.diseases,
        "documents": args.documents,
        "genes": args.genes,
        "indications": args.indications,
        "mappings": args.mappings,
        "propositions": args.propositions,
        "statements": args.statements,
        "strengths": args.strengths,
        "therapies": args.therapies,
        "therapy_groups": args.therapy_groups,
        "urls": args.urls,
    }

    dereferenced = main(input_paths=input_data)

    if args.write_concepts:
        write_all_concepts(
            input_paths=input_data,
            clear=args.clear,
            quiet=args.quiet,
        )
