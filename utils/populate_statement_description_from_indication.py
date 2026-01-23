import argparse

from utils import json_utils
from utils import read
from utils import write

def main(statements, indications):
    """
    For each statement, retrieves indication if it exists and copies the description value.

    Args:
        indications (list[dict]): List of dictionaries of database indications.
        statements (list[dict]): List of dictionaries of database statements.

    Returns:
        list[dict]: List of dictionaries of database statements, with description value copied from indications for statements associated with an indication.
    """
    for statement in statements:
        indication_id = statement.get('indication_id', None)
        if indication_id:
            indication_record = json_utils.get_record_by_key_value(records=indications, key='id', value=indication_id)
            if indication_record:
                statement['description'] = indication_record['description']
    write.records(data=statements, file="referenced/statements.json")

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog='populate_statement_description_from_indication',
        description='Statements with an associated indication will adopt the description value from the indication.'
    )
    arg_parser.add_argument(
        '--indications',
        help='json detailing db indications',
        default='referenced/indications.json'
    )
    arg_parser.add_argument(
        '--statements',
        help='json detailing db statements',
        default='referenced/statements.json'
    )
    args = arg_parser.parse_args()

    indications = read.json_records(file=args.indications)
    statements = read.json_records(file=args.statements)

    main(statements=statements, indications=indications)
