import pandas as pd

from datetime import date, timedelta

from validator import (
    check_staffing,
    check_weekly_rest,
    check_shift_overlaps
)


def sample_processes():

    return pd.DataFrame([{
        "brand_process_id": 1,
        "brand_name": "Test Brand",
        "process_name": "Customer Support",
        "working_rule": "ALL_DAYS",
        "min_staff": 1,
        "sunday_min_staff": None
    }])


def sample_assignments():

    return pd.DataFrame([{
        "employee_id": 1,
        "brand_process_id": 1,
        "start_time": "09:00",
        "end_time": "12:00"
    }])


def test_zero_coverage():

    conflicts = check_staffing(
        [date(2026, 12, 1)],
        sample_processes(),
        sample_assignments(),
        {(1, "2026-12-01"): "L"},
        set(),
        {1: "Test Employee"}
    )

    assert len(conflicts) == 1

    assert conflicts[0]["conflict_type"] == "Zero Coverage"


def test_sufficient_coverage():

    conflicts = check_staffing(
        [date(2026, 12, 1)],
        sample_processes(),
        sample_assignments(),
        {(1, "2026-12-01"): "W"},
        set(),
        {1: "Test Employee"}
    )

    assert len(conflicts) == 0


def test_insufficient_staffing():

    processes = sample_processes()

    processes.loc[0, "min_staff"] = 2

    conflicts = check_staffing(
        [date(2026, 12, 1)],
        processes,
        sample_assignments(),
        {(1, "2026-12-01"): "W"},
        set(),
        {1: "Test Employee"}
    )

    assert conflicts[0]["conflict_type"] == "Insufficient Staffing"


def test_weekly_rest_violation():

    employees = pd.DataFrame([{
        "employee_id": 1,
        "name": "Test Employee"
    }])

    dates = [
        date(2026, 12, 7) + timedelta(days=i)
        for i in range(7)
    ]

    roster = {
        (1, day.isoformat()): "W"
        for day in dates
    }

    conflicts = check_weekly_rest(
        dates, employees, roster
    )

    assert len(conflicts) == 1

    assert conflicts[0]["conflict_type"] == "Weekly Rest Violation"


def test_shift_overlap():

    processes = pd.concat([
        sample_processes(),
        sample_processes().assign(
            brand_process_id=2,
            brand_name="Second Brand"
        )
    ], ignore_index=True)

    assignments = pd.concat([
        sample_assignments(),
        sample_assignments().assign(
            brand_process_id=2,
            start_time="11:00",
            end_time="14:00"
        )
    ], ignore_index=True)

    conflicts = check_shift_overlaps(
        [date(2026, 12, 1)],
        processes,
        assignments,
        {(1, "2026-12-01"): "W"},
        set(),
        {1: "Test Employee"}
    )

    assert len(conflicts) == 1

    assert conflicts[0]["conflict_type"] == "Shift Overlap"