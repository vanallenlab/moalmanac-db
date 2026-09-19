# Postpones evaluation of type annotations so classes can be referenced before they are defined
# (avoids needing quotes around type names)
from __future__ import annotations

import argparse
import copy
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
        nullable (bool): If True, a None value in src_key is left as None instead of being looked up.
        post (typing.Callable[[dict], dict] | None): Optional function applied to the resolved record.
            Not applied when the resolved value is None.
    """

    src_key: str
    dest_key: str
    get_table: typing.Callable[[Database], BaseTable]
    nullable: bool = False
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


SUBJECT_VARIANT_PLACEHOLDER = {
    "type": "CategoricalVariant",
    "description": (
        "Placeholder. Cat-VRS does not yet support sets of categorical variants. "
        "See the 'biomarkers' extension for biomarkers associated with this Proposition."
    ),
}


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
                    if not (fk.nullable and record.get(fk.src_key) is None):
                        self.dereference_single(record, fk.src_key, table.records)
                    self.replace_key(record, fk.src_key, fk.dest_key)
                    if fk.post is not None and record[fk.dest_key] is not None:
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

    @staticmethod
    def reorder_keys(record: dict, key_order: list[str]) -> None:
        """
        Reorders a record's keys in place to match the given order.

        Args:
            record (dict): the dictionary whose keys will be reordered.
            key_order (list[str]): keys in their desired order. Keys present in `record` but not listed
                here keep their relative order and are appended after the listed keys.

        Raises:
            KeyError: If a key in `key_order` is not found in `record`.
        """
        for key in key_order:
            if key not in record:
                raise KeyError(f"Key '{key}' not found in {record}")

        remaining = [key for key in record if key not in key_order]
        reordered = {key: record[key] for key in [*key_order, *remaining]}
        record.clear()
        record.update(reordered)

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

    def write_records(self, output_dir: str, quiet: bool = False) -> None:
        """
        Writes each record in this table to its own JSON file in the given directory.

        Each file is named `{record['id']}.json`, with semicolons replaced by
        underscores and spaces replaced by dashes.

        Args:
            output_dir (str): Directory path to write the individual record files into.
            quiet (bool): Suppress print statements if True.
        """
        for record in self.records:
            filename = f"{str(record['id']).replace(':', '_').replace(' ', '-')}.json"
            path = os.path.join(output_dir, filename)
            write.dictionary(data=record, keys_list=[], file=path, quiet=quiet)


class Agents(BaseTable):
    """
    Represents the Agents table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table does not currently reference any other tables.

    Attributes:
        records (list[dict]): A list of dictionaries representing the agent records.
    """


class SequenceReferences(BaseTable):
    """
    Represents the SequenceReferences table (VRS SequenceReference objects). This class inherits common
    functionality from the BaseTable class and dereferences keys that reference other tables. This table
    does not currently reference any other tables.

    Attributes:
        records (list[dict]): A list of dictionaries representing the sequence reference records.
    """


class SequenceLocations(BaseTable):
    """
    Represents the SequenceLocations table (VRS SequenceLocation objects). This class inherits common
    functionality from the BaseTable class and dereferences keys that reference other tables. This table
    references the following tables:
    - SequenceReferences (initial key: `sequenceReference`, resulting key: `sequenceReference`)

    After foreign keys are resolved, each record's keys are reordered to `id`, `type`, `name`,
    `aliases`, `description`, `digest`, `sequenceReference`, `start`, `end`, `sequence` — `replace_key`
    moves a resolved key to the end of the dict even when its name is unchanged, so this reorder is
    needed to restore the source field order.

    Attributes:
        records (list[dict]): A list of dictionaries representing the sequence location records.
    """

    foreign_keys = [
        FKSingle(
            "sequenceReference", "sequenceReference", lambda db: db.sequence_references
        ),
    ]

    def dereference(self, db: Database) -> None:
        if self._resolved:
            return
        super().dereference(db)
        for record in self.records:
            self.reorder_keys(
                record,
                [
                    "id",
                    "type",
                    "name",
                    "aliases",
                    "description",
                    "digest",
                    "sequenceReference",
                    "start",
                    "end",
                    "sequence",
                ],
            )


class Alleles(BaseTable):
    """
    Represents the Alleles table (VRS Allele objects). This class inherits common functionality from the
    BaseTable class and dereferences keys that reference other tables. This table references the following
    tables:
    - SequenceLocations (initial key: `location`, resulting key: `location`)

    After foreign keys are resolved, the flat `hgvs.*` keys are folded into a VRS `expressions` list
    and the `state_*` keys are folded into a VRS `state` object. Each record's keys are then
    reordered to `id`, `type`, `name`, `aliases`, `description`, `digest`, `expressions`, `location`,
    `state` — `replace_key` moves a resolved key to the end of the dict even when its name is unchanged,
    so this reorder is needed to restore the source field order.

    Attributes:
        records (list[dict]): A list of dictionaries representing the allele records.
    """

    foreign_keys = [
        FKSingle("location", "location", lambda db: db.sequence_locations),
    ]

    @staticmethod
    def build_expressions(record: dict) -> None:
        """
        Folds `hgvs.g`, `hgvs.c`, `hgvs.c_short`, `hgvs.p`, and `hgvs.p_short` into an `expressions`
        list, in place.

        Each non-null `hgvs.g`, `hgvs.c`, and `hgvs.p` becomes an expression of the form
        `{"syntax": key, "value": value}`; null values are omitted, since a VRS Expression requires a
        string `value`. `hgvs.c_short` and `hgvs.p_short` are not valid VRS syntaxes, so each is attached
        as an extension, named for its referenced key, on the corresponding `hgvs.c` or `hgvs.p`
        expression. A short form with no corresponding long form is dropped, as there is no expression
        to attach it to.

        Args:
            record (dict): An allele record with flat `hgvs.*` keys.
        """
        short_forms = {
            "hgvs.c": record.pop("hgvs.c_short"),
            "hgvs.p": record.pop("hgvs.p_short"),
        }
        expressions = []
        for syntax in ("hgvs.g", "hgvs.c", "hgvs.p"):
            value = record.pop(syntax)
            if value is None:
                continue
            expression = {"syntax": syntax, "value": value}
            if short_forms.get(syntax) is not None:
                expression["extensions"] = [
                    {"name": f"{syntax}_short", "value": short_forms[syntax]},
                ]
            expressions.append(expression)
        record["expressions"] = expressions

    @staticmethod
    def build_state(record: dict) -> None:
        """
        Folds `state_type`, `state_sequence`, `state_length`, and `state_repeat_subunit_length` into
        a `state` object, in place.

        `state_type` and `state_sequence` become `type` and `sequence`. `state_length` and
        `state_repeat_subunit_length` become `length` and `repeatSubunitLength`, and are only included
        for a `ReferenceLengthExpression`, the only state type that defines them; they are null for
        all other state types.

        Args:
            record (dict): An allele record with flat `state_*` keys.
        """
        state = {
            "type": record.pop("state_type"),
            "sequence": record.pop("state_sequence"),
        }
        length = record.pop("state_length")
        repeat_subunit_length = record.pop("state_repeat_subunit_length")
        if state["type"] == "ReferenceLengthExpression":
            state["length"] = length
            state["repeatSubunitLength"] = repeat_subunit_length
        record["state"] = state

    def dereference(self, db: Database) -> None:
        if self._resolved:
            return
        super().dereference(db)
        for record in self.records:
            self.build_expressions(record)
            self.build_state(record)
            self.reorder_keys(
                record,
                [
                    "id",
                    "type",
                    "name",
                    "aliases",
                    "description",
                    "digest",
                    "expressions",
                    "location",
                    "state",
                ],
            )


def is_fusion(record: dict) -> bool:
    """
    Checks whether a biomarker record's extensions mark it as a gene fusion.

    Args:
        record (dict): A biomarker record with an `extensions` list.

    Returns:
        bool: True if the record has a `rearrangement_type` extension valued "Fusion".
    """
    return any(
        extension["name"] == "rearrangement_type" and extension["value"] == "Fusion"
        for extension in record["extensions"]
    )


class Biomarkers(BaseTable):
    """
    Represents the Biomarkers table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables, then shapes the resolved allele, location, genes, and
    copy change into Cat-VRS constraint objects. This table references the following tables:
    - Alleles (initial key: `allele`, resulting key: `allele`)
    - SequenceLocations (initial key: `location`, resulting key: `location`)
    - Genes (initial key: `genes`, resulting key: `genes`)
    - CopyChanges (initial key: `copyChange`, resulting key: `copyChange`)

    The dereferenced allele, when present, is wrapped as a `DefiningAlleleConstraint`. The dereferenced
    location, when present, is wrapped as a `DefiningLocationConstraint` (used for biomarkers defined
    against a gene's whole protein product rather than a specific allele). For most records, each
    dereferenced gene is wrapped as a `FeatureContextConstraint`. For gene fusions (`rearrangement_type`
    extension equal to "Fusion"), the resolved genes are instead collapsed into a single
    `AdjacencyConstraint`, with `orderKnown` set based on whether both fusion partners are known; a
    fusion with only one known partner gets a trailing `UnspecifiedElement` for the other. Each
    gene has its `extensions` stripped before embedding (`Genes.build_extensions` output is only meant
    for a gene's own standalone/per-concept record). The dereferenced copy change, when present, is
    wrapped as a `CopyChangeConstraint`. All resulting constraints are merged into a single `constraints`
    list.

    Attributes:
        records (list[dict]): A list of dictionaries representing the biomarker records.
    """

    foreign_keys = [
        FKSingle(
            "allele",
            "allele",
            lambda db: db.alleles,
            nullable=True,
            post=lambda record: {
                "type": "DefiningAlleleConstraint",
                "allele": record,
                "relations": [],
            },
        ),
        FKSingle(
            "location",
            "location",
            lambda db: db.sequence_locations,
            nullable=True,
            post=lambda record: {
                "type": "DefiningLocationConstraint",
                "location": record,
                "relations": [],
                "matchCharacteristic": {
                    "primaryCoding": {
                        "code": "is_within",
                        "system": "ga4gh-gks-term:location-match",
                    },
                },
            },
        ),
        FKList("genes", "genes", lambda db: db.genes, post=strip_keys("extensions")),
        FKSingle(
            "copyChange",
            "copyChange",
            lambda db: db.copy_change,
            nullable=True,
            post=lambda record: {
                "type": "CopyChangeConstraint",
                "copyChange": record["name"],
            },
        ),
    ]

    def wrap_constraints(self) -> None:
        """
        Wraps each record's dereferenced allele, location, genes, and copy change into Cat-VRS
        constraint objects.

        The allele, when present, becomes a `DefiningAlleleConstraint`. The location, when present,
        becomes a `DefiningLocationConstraint`. Non-fusion records get one `FeatureContextConstraint`
        per gene. Fusion records collapse their genes into a single `AdjacencyConstraint`, with
        `orderKnown` True only when both fusion partners are known (two genes); a single-gene fusion
        has an `UnspecifiedElement` appended to `adjoinedElements` for the unknown partner. The copy change, when
        present, becomes a `CopyChangeConstraint`. All resulting constraints are merged into a single
        `constraints` list.
        """
        for record in self.records:
            allele_constraint = record.pop("allele")
            location_constraint = record.pop("location")
            genes = record.pop("genes")
            copy_change = record.pop("copyChange")
            if is_fusion(record):
                adjoined_elements = list(genes)
                if len(genes) == 1:
                    adjoined_elements.append({"type": "UnspecifiedElement"})
                gene_constraints = [
                    {
                        "type": "AdjacencyConstraint",
                        "orderKnown": len(genes) == 2,
                        "adjoinedElements": adjoined_elements,
                    },
                ]
            else:
                gene_constraints = [
                    {"type": "FeatureContextConstraint", "featureContext": gene}
                    for gene in genes
                ]
            allele_constraints = [allele_constraint] if allele_constraint else []
            location_constraints = [location_constraint] if location_constraint else []
            copy_changes = [copy_change] if copy_change else []
            record["constraints"] = (
                allele_constraints
                + location_constraints
                + gene_constraints
                + copy_changes
            )

    def dereference(self, db: Database) -> None:
        """
        Dereferences all referenced keys within the Biomarkers table, then wraps genes into constraints.

        Resolves foreign keys declared in `foreign_keys` via the base class, then applies
        `wrap_constraints`. Each table is resolved at most once; subsequent calls are no-ops.

        Args:
            db (Database): An instance of the Database class containing all tables.
        """
        if self._resolved:
            return
        super().dereference(db)
        self.wrap_constraints()
        for record in self.records:
            self.reorder_keys(
                record, ["id", "type", "name", "constraints", "extensions"]
            )


class BiomarkerCriteria(BaseTable):
    """
    Represents the BiomarkerCriteria table, an interim biomarker-to-proposition link
    (a draft Cat-VRS "categorical variant criterion"). Each record pairs a biomarker
    with a `present` flag describing whether that biomarker is asserted present or
    absent in the referencing proposition. This class inherits common functionality
    from the BaseTable class and references the following tables:
    - Biomarkers (initial key: `subject`, resulting key: `subject`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the criterion records.
    """

    foreign_keys = [
        FKSingle("subject", "subject", lambda db: db.biomarkers),
    ]


class Codings(BaseTable):
    """
    Represents the Codings table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table does not currently reference any other tables.

    Attributes:
        records (list[dict]): A list of dictionaries representing the coding records.
    """


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


class CopyChanges(BaseTable):
    """
    Represents the CopyChanges table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table does not currently reference any other tables.

    Attributes:
        records (list[dict]): A list of dictionaries representing the copy change records.
    """


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
            "agent_id",
            "agent",
            lambda db: db.agents,
            post=strip_keys("extensions"),
        ),
        FKList(
            "urls",
            "urls",
            lambda db: db.urls,
            post=extract_url_value,
        ),
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
    - SequenceLocations (initial key: `protein_product`, resulting key: `protein_product`)
    - SequenceLocations (initial key: `protein_product_exons`, resulting key: `protein_product_exons`)
    - SequenceLocations (initial key: `transcript`, resulting key: `transcript`)
    - SequenceLocations (initial key: `transcript_exons`, resulting key: `transcript_exons`)

    After foreign keys are resolved, `cds_start`, `location`, `location_sortable`, `protein_product`,
    `protein_product_exons`, `transcript`, and `transcript_exons` are folded into an `extensions` list
    (see `build_extensions`), and each record's keys are reordered to `id`, `conceptType`, `name`,
    `primaryCoding`, `mappings`, `extensions`.

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
        FKSingle(
            "protein_product", "protein_product", lambda db: db.sequence_locations
        ),
        FKList(
            "protein_product_exons",
            "protein_product_exons",
            lambda db: db.sequence_locations,
        ),
        FKSingle("transcript", "transcript", lambda db: db.sequence_locations),
        FKList(
            "transcript_exons", "transcript_exons", lambda db: db.sequence_locations
        ),
    ]

    def build_extensions(self) -> None:
        """
        Folds `cds_start`, `location`, `location_sortable`, `protein_product`,
        `protein_product_exons`, `transcript`, and `transcript_exons` into an `extensions` list,
        in place.

        `protein_product`, `protein_product_exons`, `transcript`, and `transcript_exons` are already
        dereferenced SequenceLocation objects by the time this runs. This only runs on the Genes
        table's own records, so it produces the richer standalone/per-concept form; a gene embedded
        elsewhere (e.g. via Biomarkers' `genes` foreign key) has this `extensions` list stripped at
        the embedding site instead.
        """
        for record in self.records:
            cds_start = record.pop("cds_start")
            location = record.pop("location")
            location_sortable = record.pop("location_sortable")
            protein_product = record.pop("protein_product")
            protein_product_exons = record.pop("protein_product_exons")
            transcript = record.pop("transcript")
            transcript_exons = record.pop("transcript_exons")
            record["extensions"] = [
                {"name": "cds_start", "value": cds_start},
                {"name": "location", "value": location},
                {"name": "location_sortable", "value": location_sortable},
                {"name": "protein_product", "value": protein_product},
                {"name": "protein_product_exons", "value": protein_product_exons},
                {"name": "transcript", "value": transcript},
                {"name": "transcript_exons", "value": transcript_exons},
            ]

    def dereference(self, db: Database) -> None:
        """
        Dereferences all referenced keys within the Genes table, then reorders each record's keys.

        Resolves foreign keys declared in `foreign_keys` via the base class, folds `cds_start`,
        `location`, `location_sortable`, `protein_product`, `protein_product_exons`, `transcript`,
        and `transcript_exons` into an `extensions` list via `build_extensions`, then reorders keys
        to `id`, `conceptType`, `name`, `primaryCoding`, `mappings`, `extensions`. Each table is
        resolved at most once; subsequent calls are no-ops.

        Args:
            db (Database): An instance of the Database class containing all tables.
        """
        if self._resolved:
            return
        super().dereference(db)
        self.build_extensions()
        for record in self.records:
            self.reorder_keys(
                record,
                [
                    "id",
                    "conceptType",
                    "name",
                    "primaryCoding",
                    "mappings",
                    "extensions",
                ],
            )


class Indications(BaseTable):
    """
    Represents the Indications table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - Contributions (initial key: `contributions`, resulting key: `contributions`)
    - Documents (initial key: `reportedIn`, resulting key: `reportedIn`)

    After foreign keys are resolved, table-specific fields (`status` and, for HSE
    indications, `reimbursement_scheme` and `reimbursement_comment`) are converted to
    extensions and the remaining referenced-only fields are dropped.

    Attributes:
        records (list[dict]): A list of dictionaries representing the indication records.
    """

    foreign_keys = [
        FKList("contributions", "contributions", lambda db: db.contributions),
        FKList("reportedIn", "reportedIn", lambda db: db.documents),
    ]

    def convert_fields_to_extensions(self) -> None:
        """
        Converts relevant keys to extensions
        """

        extension_fields = [
            "status",
            "superseded_by",
            "reimbursement_scheme",
            "reimbursement_comment",
        ]

        for record in self.records:
            extensions = [
                {
                    "name": "status",
                    "value": record["status"],
                    "description": "Current approval status.",
                },
            ]
            if str(record["id"]).startswith("ind:hse:"):
                extensions.append(
                    {
                        "name": "reimbursement_scheme",
                        "value": record["reimbursement_scheme"],
                        "description": "Current scheme used to reimburse indication.",
                    }
                )
                extensions.append(
                    {
                        "name": "reimbursement_comment",
                        "value": record["reimbursement_comment"],
                        "description": (
                            "More details about the current reimbursement scheme(s)."
                        ),
                    }
                )
            record["extensions"] = extensions
            for field in extension_fields:
                if field in record:
                    self.remove_key(record=record, key=field)

    def dereference(self, db: Database) -> None:
        """
        Dereferences all referenced keys within the Indications table, then converts fields
        to extensions.

        Args:
            db (Database): An instance of the Database class containing all tables.
        """
        if self._resolved:
            return
        super().dereference(db)
        self.convert_fields_to_extensions()
        self.remove_keys()

    def remove_keys(self) -> None:
        fields_to_remove = [
            "statement_description",
            "raw_biomarkers",
            "raw_cancer_types",
            "raw_therapeutics",
        ]
        for record in self.records:
            for field in fields_to_remove:
                self.remove_key(record=record, key=field)


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

    def dereference(self, db: Database) -> None:
        """
        Dereferences `coding_id`, then removes `primary_coding_id`, which is the join table's foreign key
        and is not part of the GKM Core concept mapping.

        Args:
            db (Database): An instance of the Database class containing all tables.
        """
        super().dereference(db)
        self.records = [strip_keys("primary_coding_id")(r) for r in self.records]


class Propositions(BaseTable):
    """
    Represents the Propositions table. This class inherits common functionality from the BaseTable class and
    dereferences keys that reference other tables. This table references the following tables:
    - BiomarkerCriteria (initial key: `biomarker_criteria`, resulting key: `biomarkers`; each
      element is the dereferenced criterion record, i.e. `{id, subject, present}` with
      `subject` itself resolved to the full biomarker record). Since Cat-VRS does not yet support
      sets of categorical variants, `biomarkers` is then moved into an extension of the same name
      and `subjectVariant` is set to `SUBJECT_VARIANT_PLACEHOLDER`.
    - Diseases (initial key: `conditionQualifier_id`, resulting key: `conditionQualifier`)
    - Therapies (initial key: `therapy_id`, resulting key: `objectTherapeutic`)
    - TherapyGroups (initial_key: `therapy_group_id`, resulting key: `objectTherapeutic`)

    Attributes:
        records (list[dict]): A list of dictionaries representing the proposition records.
    """

    foreign_keys = [
        FKSingle("conditionQualifier_id", "conditionQualifier", lambda db: db.diseases),
        FKList(
            "biomarker_criteria",
            "biomarkers",
            lambda db: db.biomarker_criteria,
        ),
    ]

    def convert_fields_to_extensions(self) -> None:
        """
        Moves the dereferenced `biomarkers` into a `biomarkers` extension and adds the placeholder `subjectVariant`.

        Each record is rebuilt in place with the key order `id`, `type`, `predicate`, `subjectVariant`,
        `conditionQualifier`, `objectTherapeutic`, `extensions`, followed by any other keys.
        """
        leading_keys = ["id", "type", "predicate"]
        middle_keys = ["conditionQualifier", "objectTherapeutic"]
        for record in self.records:
            extensions = [
                {
                    "name": "biomarkers",
                    "value": record.pop("biomarkers"),
                    "description": (
                        "The biomarkers associated with this Proposition, each with a `present` flag "
                        "indicating if the biomarker is present (true) or absent (false). "
                        "Multiple biomarkers are combined with implied AND logic."
                    ),
                },
            ]
            ordered = {key: record.pop(key) for key in leading_keys}
            ordered["subjectVariant"] = copy.deepcopy(SUBJECT_VARIANT_PLACEHOLDER)
            for key in middle_keys:
                ordered[key] = record.pop(key)
            ordered.update(record)
            ordered["extensions"] = extensions
            record.clear()
            record.update(ordered)

    def dereference(self, db: Database) -> None:
        """
        Dereferences all referenced keys within the Propositions table.

        Resolves therapies and therapy groups before delegating FK resolution to the base class,
        then applies the custom therapeutics dereferencing and converts `biomarkers` to an extension.
        Each table is resolved at most once; subsequent calls are no-ops.

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
        self.convert_fields_to_extensions()

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
            if isinstance(record["therapy_id"], str):
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
            elif isinstance(record["therapy_group_id"], str):
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

    After foreign keys are resolved, `status` and the dereferenced `indication`
    record are converted to extensions.

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

    def convert_fields_to_extensions(self) -> None:
        """
        Converts `status` and the dereferenced `indication` record to extensions.
        """
        extension_fields = ["status", "indication"]
        for record in self.records:
            extensions = [
                {
                    "name": "status",
                    "value": record["status"],
                    "description": (
                        "Whether this Statement is Active, Superseded, or Deprecated within moalmanac-db."
                    ),
                },
                {
                    "name": "indication",
                    "value": record["indication"],
                    "description": (
                        "The underlying Indication supporting this Statement."
                    ),
                },
            ]
            record["extensions"] = extensions
            for field in extension_fields:
                if field in record:
                    self.remove_key(record=record, key=field)

    def dereference(self, db: Database) -> None:
        """
        Dereferences all referenced keys within the Statements table, then converts
        `status` and the dereferenced `indication` to extensions.

        Args:
            db (Database): An instance of the Database class containing all tables.
        """
        if self._resolved:
            return
        super().dereference(db)
        self.convert_fields_to_extensions()


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


@dataclasses.dataclass
class Database:
    """
    A container holding all table instances for the relational database.

    Attributes:
        agents (Agents): An instance of the Agents class.
        alleles (Alleles): An instance of the Alleles class.
        biomarkers (Biomarkers): An instance of the Biomarkers class.
        biomarker_criteria (BiomarkerCriteria): An instance of the BiomarkerCriteria class.
        codings (Codings): An instance of the Codings class.
        contributions (Contributions): An instance of the Contributions class.
        copy_change (CopyChanges): An instance of the CopyChanges class.
        diseases (Diseases): An instance of the Diseases class.
        documents (Documents): An instance of the Documents class.
        genes (Genes): An instance of the Genes class.
        indications (Indications): An instance of the Indications class.
        mappings (Mappings): An instance of the Mappings class.
        propositions (Propositions): An instance of the Propositions class.
        sequence_locations (SequenceLocations): An instance of the SequenceLocations class.
        sequence_references (SequenceReferences): An instance of the SequenceReferences class.
        statements (Statements): An instance of the Statements class.
        strengths (Strengths): An instance of the Strengths class.
        therapies (Therapies): An instance of the Therapies class.
        therapy_groups (TherapyGroups): An instance of the TherapyGroups class.
        urls (URLs): An instance of the URLs class.
    """

    agents: Agents
    alleles: Alleles
    biomarkers: Biomarkers
    biomarker_criteria: BiomarkerCriteria
    codings: Codings
    contributions: Contributions
    copy_change: CopyChanges
    diseases: Diseases
    documents: Documents
    genes: Genes
    indications: Indications
    mappings: Mappings
    propositions: Propositions
    sequence_locations: SequenceLocations
    sequence_references: SequenceReferences
    statements: Statements
    strengths: Strengths
    therapies: Therapies
    therapy_groups: TherapyGroups
    urls: URLs


def populate_statements_from_indications(
    statements: list[dict],
    indications: list[dict],
) -> list[dict]:
    """
    Propagates `description`, `reportedIn`, and `contributions` from each indication onto the
    statements associated with it, so that an indication and its statements carry identical
    values. The statement `description` is taken from the indication's `statement_description`.

    Args:
        indications (list[dict]): List of dictionaries of database indications.
        statements (list[dict]): List of dictionaries of database statements.

    Returns:
        list[dict]: List of dictionaries of database statements, with `description`,
        `reportedIn`, and `contributions` copied from the associated indication.
    """
    for statement in statements:
        indication_id = statement.get("indication_id", None)
        if indication_id:
            indication_record = json_utils.get_record_by_key_value(
                records=indications, key="id", value=indication_id
            )
            if indication_record:
                statement["description"] = indication_record["statement_description"]
                statement["reportedIn"] = list(indication_record["reportedIn"])
                statement["contributions"] = list(indication_record["contributions"])
    write.records(
        data=statements,
        file=os.path.join("referenced", "statements.json"),
    )
    return statements


def populate_statement_status(
    statements: list[dict],
    indications: list[dict],
) -> list[dict]:
    """
    Populates the status field for statements from the status field from the associated indication.

    Args:
        indications (list[dict]): List of dictionaries of database indications.
        statements (list[dict]): List of dictionaries of database statements.

    Returns:
        list[dict]: List of dictionaries of database statements, with status value copied from indications for statements associated with an indication.
    """
    status_map = {
        "Approved": "Active",
        "Accelerated": "Active",
        "Superseded": "Superseded",
        "Withdrawn": "Deprecated",
    }

    for statement in statements:
        indication_id = statement.get("indication_id", None)
        if indication_id:
            indication_record = json_utils.get_record_by_key_value(
                records=indications, key="id", value=indication_id
            )
            if indication_record:
                statement["status"] = status_map.get(indication_record["status"])
        if "indication_id" in statement:
            statement["indication_id"] = statement.pop("indication_id")
    write.records(
        data=statements,
        file=os.path.join("referenced", "statements.json"),
    )
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
    ("alleles", os.path.join("dereferenced", "alleles")),
    ("biomarkers", os.path.join("dereferenced", "biomarkers")),
    ("biomarker_criteria", os.path.join("dereferenced", "biomarker_criteria")),
    ("codings", os.path.join("dereferenced", "codings")),
    ("contributions", os.path.join("dereferenced", "contributions")),
    ("copy_change", os.path.join("dereferenced", "copy_change")),
    ("diseases", os.path.join("dereferenced", "diseases")),
    ("documents", os.path.join("dereferenced", "documents")),
    ("genes", os.path.join("dereferenced", "genes")),
    ("indications", os.path.join("dereferenced", "indications")),
    ("mappings", os.path.join("dereferenced", "mappings")),
    ("propositions", os.path.join("dereferenced", "propositions")),
    ("sequence_locations", os.path.join("dereferenced", "sequence_locations")),
    ("sequence_references", os.path.join("dereferenced", "sequence_references")),
    ("statements", os.path.join("dereferenced", "statements")),
    ("strengths", os.path.join("dereferenced", "strengths")),
    ("therapies", os.path.join("dereferenced", "therapies")),
    ("therapy_groups", os.path.join("dereferenced", "therapy_groups")),
]


def write_all_concepts(
    input_paths: dict, clear: bool = False, quiet: bool = False
) -> None:
    """
    Writes per-concept JSON files for all entity types in `_CONCEPT_DIRS` to their output directories.

    Constructs a fresh Database from the raw input files (independent of any already-resolved
    full-DB tables), dereferences each entity, and writes one JSON file per record to
    `dereferenced/<entity>/<id>.json`.

    Semicolons in <id> will be replaced with underscores and spaces will be replaced with dashes.

    Args:
        input_paths (dict): Dictionary of paths to referenced JSON files.
        clear (bool): If True, remove existing JSON files from each output directory first.
        quiet (bool): Suppress print statements if True.
    """
    if clear:
        for _, output_dir in _CONCEPT_DIRS:
            clear_output_dir(output_dir, quiet=quiet)

    db = Database(
        agents=Agents(
            records=read.json_records(file=input_paths["agents"]),
        ),
        alleles=Alleles(
            records=read.json_records(file=input_paths["alleles"]),
        ),
        biomarkers=Biomarkers(
            records=read.json_records(file=input_paths["biomarkers"])
        ),
        biomarker_criteria=BiomarkerCriteria(
            records=read.json_records(file=input_paths["biomarker_criteria"])
        ),
        codings=Codings(
            records=read.json_records(file=input_paths["codings"]),
        ),
        contributions=Contributions(
            records=read.json_records(file=input_paths["contributions"])
        ),
        copy_change=CopyChanges(
            records=read.json_records(file=input_paths["copy_change"]),
        ),
        diseases=Diseases(
            records=read.json_records(file=input_paths["diseases"]),
        ),
        documents=Documents(
            records=read.json_records(file=input_paths["documents"]),
        ),
        genes=Genes(
            records=read.json_records(file=input_paths["genes"]),
        ),
        indications=Indications(
            records=read.json_records(file=input_paths["indications"])
        ),
        mappings=Mappings(
            records=read.json_records(file=input_paths["mappings"]),
        ),
        propositions=Propositions(
            records=read.json_records(file=input_paths["propositions"])
        ),
        sequence_locations=SequenceLocations(
            records=read.json_records(file=input_paths["sequence_locations"]),
        ),
        sequence_references=SequenceReferences(
            records=read.json_records(file=input_paths["sequence_references"]),
        ),
        statements=Statements(
            records=read.json_records(file=input_paths["statements"])
        ),
        strengths=Strengths(
            records=read.json_records(file=input_paths["strengths"]),
        ),
        therapies=Therapies(
            records=read.json_records(file=input_paths["therapies"]),
        ),
        therapy_groups=TherapyGroups(
            records=read.json_records(file=input_paths["therapy_groups"])
        ),
        urls=URLs(
            records=read.json_records(file=input_paths["urls"]),
        ),
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
    alleles = read.json_records(file=input_paths["alleles"])
    biomarkers = read.json_records(file=input_paths["biomarkers"])
    biomarker_criteria = read.json_records(file=input_paths["biomarker_criteria"])
    codings = read.json_records(file=input_paths["codings"])
    contributions = read.json_records(file=input_paths["contributions"])
    copy_change = read.json_records(file=input_paths["copy_change"])
    diseases = read.json_records(file=input_paths["diseases"])
    documents = read.json_records(file=input_paths["documents"])
    genes = read.json_records(file=input_paths["genes"])
    indications = read.json_records(file=input_paths["indications"])
    mappings = read.json_records(file=input_paths["mappings"])
    propositions = read.json_records(file=input_paths["propositions"])
    sequence_locations = read.json_records(file=input_paths["sequence_locations"])
    sequence_references = read.json_records(file=input_paths["sequence_references"])
    statements = read.json_records(file=input_paths["statements"])
    strengths = read.json_records(file=input_paths["strengths"])
    therapies = read.json_records(file=input_paths["therapies"])
    therapy_groups = read.json_records(file=input_paths["therapy_groups"])
    urls = read.json_records(file=input_paths["urls"])

    statements = populate_statements_from_indications(
        indications=indications,
        statements=statements,
    )
    statements = populate_statement_status(
        indications=indications,
        statements=statements,
    )

    # Step 2: Generate table objects
    agents = Agents(records=agents)
    alleles = Alleles(records=alleles)
    biomarkers = Biomarkers(records=biomarkers)
    biomarker_criteria = BiomarkerCriteria(records=biomarker_criteria)
    codings = Codings(records=codings)
    contributions = Contributions(records=contributions)
    copy_change = CopyChanges(records=copy_change)
    diseases = Diseases(records=diseases)
    documents = Documents(records=documents)
    genes = Genes(records=genes)
    indications = Indications(records=indications)
    mappings = Mappings(records=mappings)
    propositions = Propositions(records=propositions)
    sequence_locations = SequenceLocations(records=sequence_locations)
    sequence_references = SequenceReferences(records=sequence_references)
    statements = Statements(records=statements)
    strengths = Strengths(records=strengths)
    therapies = Therapies(records=therapies)
    therapy_groups = TherapyGroups(records=therapy_groups)
    urls = URLs(records=urls)

    # Step 3: Dereference the database and generate statements
    db = Database(
        agents=agents,
        alleles=alleles,
        biomarkers=biomarkers,
        biomarker_criteria=biomarker_criteria,
        codings=codings,
        contributions=contributions,
        copy_change=copy_change,
        diseases=diseases,
        documents=documents,
        genes=genes,
        indications=indications,
        mappings=mappings,
        propositions=propositions,
        sequence_locations=sequence_locations,
        sequence_references=sequence_references,
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
        "--alleles",
        help="json detailing db alleles",
        default=os.path.join("referenced", "alleles.json"),
    )
    arg_parser.add_argument(
        "--biomarkers",
        help="json detailing db biomarkers",
        default=os.path.join("referenced", "biomarkers.json"),
    )
    arg_parser.add_argument(
        "--biomarker-criteria",
        help="json detailing db biomarker criteria",
        default=os.path.join("referenced", "biomarker_criteria.json"),
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
        "--copy-change",
        help="json detailing db copy changes",
        default=os.path.join("referenced", "copy_changes.json"),
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
        "--sequence-locations",
        help="json detailing db sequence locations",
        default=os.path.join("referenced", "sequence_locations.json"),
    )
    arg_parser.add_argument(
        "--sequence-references",
        help="json detailing db sequence references",
        default=os.path.join("referenced", "sequence_references.json"),
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
        "alleles": args.alleles,
        "biomarkers": args.biomarkers,
        "biomarker_criteria": args.biomarker_criteria,
        "codings": args.codings,
        "contributions": args.contributions,
        "copy_change": args.copy_change,
        "diseases": args.diseases,
        "documents": args.documents,
        "genes": args.genes,
        "indications": args.indications,
        "mappings": args.mappings,
        "propositions": args.propositions,
        "sequence_locations": args.sequence_locations,
        "sequence_references": args.sequence_references,
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
