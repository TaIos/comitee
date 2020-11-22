import pytest

from committee.committee import __fetch_all_commits
from helpers import *


@pytest.mark.parametrize(["reposlug", "author", "path", "ref"], [("LQpKH20/committee-basic", None, None, None)])
def test_fetch_all_commits(session, reposlug, author, path, ref):
    """Test that for a given setup described in README all commits are fetched correctly"""
    r = __fetch_all_commits(session, reposlug, author, path, ref)
    assert isinstance(r, list)
    assert len(r) == 4
    assert isinstance(r[0], dict)
    assert isinstance(r[1], dict)
    assert isinstance(r[2], dict)
    assert isinstance(r[3], dict)
