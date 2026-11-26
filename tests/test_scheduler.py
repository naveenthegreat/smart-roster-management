from datetime import date

from scheduler import (
    get_month_dates,
    is_process_open,
    get_required_staff
)


def test_december_dates():

    dates = get_month_dates(2026, 12)

    assert len(dates) == 31


def test_leap_year():

    dates = get_month_dates(2028, 2)

    assert len(dates) == 29


def test_normal_february():

    dates = get_month_dates(2026, 2)

    assert len(dates) == 28


def test_all_days_rule():

    process = {
        "working_rule": "ALL_DAYS"
    }

    assert is_process_open(
        process,
        date(2026, 12, 6),
        set()
    )


def test_sunday_closed():

    process = {
        "working_rule": "NO_SUNDAY_HOLIDAYS"
    }

    assert not is_process_open(
        process,
        date(2026, 12, 6),
        set()
    )


def test_public_holiday_closed():

    process = {
        "working_rule": "NO_HOLIDAYS"
    }

    assert not is_process_open(
        process,
        date(2026, 12, 25),
        {"2026-12-25"}
    )


def test_default_staffing():

    process = {
        "brand_process_id": 1,
        "min_staff": 2,
        "sunday_min_staff": None
    }

    assert get_required_staff(
        process,
        date(2026, 12, 1),
        {}
    ) == 2


def test_sunday_staffing():

    process = {
        "brand_process_id": 1,
        "min_staff": 3,
        "sunday_min_staff": 1
    }

    assert get_required_staff(
        process,
        date(2026, 12, 6),
        {}
    ) == 1


def test_custom_weekday_staffing():

    process = {
        "brand_process_id": 1,
        "min_staff": 2,
        "sunday_min_staff": None
    }

    rules = {
        (1, 1): 4
    }

    assert get_required_staff(
        process,
        date(2026, 12, 1),
        rules
    ) == 4