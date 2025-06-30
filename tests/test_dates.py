import pytest

def test_accessed_after_publication_date(data):
    """
    Ensure that the accessed date is more recent than the publication date for each document.
    """
    failed = [
        doc for doc in data['documents']
        if doc.get('access_date') and doc.get('publication_date')
           and doc.get('access_date') < doc.get('publication_date')
    ]
    error_message = (
    f"Entered access date is prior to the publication date:\n"
    f"  - Document ids: {', '.join([doc['id'] for doc in failed])}\n"
    f"  - Total affected: {len(failed)}"
    )
    assert not failed, error_message

@pytest.mark.skip(reason="Not implemented yet")
def test_last_updated_after_publication_date(data):
    """
    Ensure that the last_updated date is more recent than the publication date for each document.
    """
