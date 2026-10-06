def test_indication_contributions_ordered_by_date(data):
    """
    Ensures that each indication lists its contributions in descending date order.
    """
    contribution_dates = {r['id']: r['date'] for r in data['contributions']}
    failed_records = []
    for record in data['indications']:
        dates = [contribution_dates[c] for c in record['contributions']]
        if dates != sorted(dates, reverse=True):
            failed_records.append(record['id'])

    assert not failed_records, (
        f"Indications with contributions not ordered by date descending: "
        f"{failed_records}"
    )

def test_statement_contributions_ordered_by_date(data):
    """
    Ensures that each statement lists its contributions in descending date order.
    """
    contribution_dates = {r['id']: r['date'] for r in data['contributions']}
    failed_records = []
    for record in data['statements']:
        dates = [contribution_dates[c] for c in record['contributions']]
        if dates != sorted(dates, reverse=True):
            failed_records.append(record['id'])

    assert not failed_records, (
        f"Statements with contributions not ordered by date descending: "
        f"{failed_records}"
    )
