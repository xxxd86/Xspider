from cleaning.deduplicate import deduplicate
from cleaning.filter_invalid import filter_invalid
from cleaning.normalise import normalize_content


def test_cleaning_pipeline():
    records = [
        {"source": "wechat", "company": "Acme", "content": "Hello   World"},
        {"source": "wechat", "company": "Acme", "content": "Hello   World"},
        {"source": "wechat", "company": "Acme", "content": ""},
    ]

    normalised = normalize_content(records)
    filtered = filter_invalid(normalised)
    unique = deduplicate(filtered)

    assert len(filtered) == 2
    assert len(unique) == 1
    assert unique[0]["content"] == "Hello World"
