import pandas as pd

from roster_editor import compare_conflicts


COLUMNS = [
    "date",
    "conflict_type",
    "severity",
    "brand",
    "process",
    "employee",
    "description",
    "suggestion"
]


def sample_conflict():

    return pd.DataFrame([[
        "2026-12-01",
        "Zero Coverage",
        "Critical",
        "Test Brand",
        "Customer Support",
        "Test Employee",
        "No employee available",
        "Assign backup"
    ]], columns=COLUMNS)


def test_new_conflict():

    before = pd.DataFrame(columns=COLUMNS)

    after = sample_conflict()

    new, resolved = compare_conflicts(
        before, after
    )

    assert len(new) == 1

    assert len(resolved) == 0


def test_resolved_conflict():

    before = sample_conflict()

    after = pd.DataFrame(columns=COLUMNS)

    new, resolved = compare_conflicts(
        before, after
    )

    assert len(new) == 0

    assert len(resolved) == 1


def test_unchanged_conflicts():

    before = sample_conflict()

    after = sample_conflict()

    new, resolved = compare_conflicts(
        before, after
    )

    assert len(new) == 0

    assert len(resolved) == 0