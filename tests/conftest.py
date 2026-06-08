import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def bug_payload():
    return load_fixture("bug_40000.json")


@pytest.fixture
def comments_payload():
    return load_fixture("bug_40000_comment.json")


@pytest.fixture
def search_payload():
    return load_fixture("quicksearch_logrotate.json")
