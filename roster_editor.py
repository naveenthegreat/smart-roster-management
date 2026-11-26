import pandas as pd

from database import get_connection
from validator import validate_roster
from ui_helpers import read_data


VALID_STATUSES = ["W", "O", "L", "H", "C", "U"]


def get_current_status(employee_id, work_date):

    result = read_data("""
        SELECT status
        FROM roster
        WHERE employee_id = ?
        AND work_date = ?
    """, (int(employee_id), str(work_date)))

    if result.empty:
        return None

    return result.iloc[0]["status"]

def check_edit_allowed(employee_id, work_date, new_status):

    if new_status not in VALID_STATUSES:
        return False, "Invalid roster status."

    employee = read_data("""
        SELECT *
        FROM employees
        WHERE employee_id = ?
    """, (int(employee_id),))

    if employee.empty:
        return False, "Employee does not exist."

    leave = read_data("""
        SELECT leave_type
        FROM leaves
        WHERE employee_id = ?
        AND leave_date = ?
    """, (int(employee_id), str(work_date)))

    if not leave.empty:

        required_status = leave.iloc[0]["leave_type"]

        if new_status != required_status:

            return False, (
                "This employee has approved leave, "
                "comp-off or unavailability on this date."
            )

    else:

        holiday = read_data("""
            SELECT *
            FROM holidays
            WHERE holiday_date = ?
        """, (str(work_date),))

        if (
            not holiday.empty
            and employee.iloc[0]["holiday_off"] == 1
            and new_status != "H"
        ):

            return False, (
                "This employee has a mandatory "
                "public holiday off."
            )

        if new_status == "H" and (
            holiday.empty
            or employee.iloc[0]["holiday_off"] != 1
        ):
            return False, "No applicable public holiday."

    return True, "Change allowed."

def compare_conflicts(before, after):

    key_columns = [
        "date",
        "conflict_type",
        "severity",
        "brand",
        "process",
        "employee",
        "description"
    ]

    before_keys = set(
        before[key_columns].itertuples(
            index=False, name=None
        )
    )

    after_keys = set(
        after[key_columns].itertuples(
            index=False, name=None
        )
    )

    new_keys = after_keys - before_keys

    resolved_keys = before_keys - after_keys

    new_conflicts = after[
        [
            row in new_keys
            for row in after[key_columns].itertuples(
                index=False, name=None
            )
        ]
    ].copy() if not after.empty else after.copy()

    resolved_conflicts = before[
        [
            row in resolved_keys
            for row in before[key_columns].itertuples(
                index=False, name=None
            )
        ]
    ].copy() if not before.empty else before.copy()

    return new_conflicts, resolved_conflicts

def preview_roster_change(
    year, month, employee_id,
    work_date, new_status
):

    current_status = get_current_status(
        employee_id, work_date
    )

    if current_status is None:
        raise ValueError("Roster entry does not exist.")

    allowed, message = check_edit_allowed(
        employee_id, work_date, new_status
    )

    if not allowed:
        raise ValueError(message)

    before = validate_roster(year, month)

    overrides = {
        (int(employee_id), str(work_date)): new_status
    }

    after = validate_roster(
        year, month,
        overrides=overrides
    )

    new_conflicts, resolved_conflicts = (
        compare_conflicts(before, after)
    )

    return {
        "current_status": current_status,
        "new_status": new_status,
        "before": before,
        "after": after,
        "new_conflicts": new_conflicts,
        "resolved_conflicts": resolved_conflicts
    }

def update_roster_status(
    employee_id,
    work_date,
    new_status,
    expected_status
):

    allowed, message = check_edit_allowed(
        employee_id, work_date, new_status
    )

    if not allowed:
        raise ValueError(message)

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""
            UPDATE roster
            SET status = ?
            WHERE employee_id = ?
            AND work_date = ?
            AND status = ?
        """, (
            new_status,
            int(employee_id),
            str(work_date),
            expected_status
        ))

        if cursor.rowcount == 0:
            raise ValueError(
                "Roster entry changed or no longer exists. "
                "Preview the change again."
            )

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()

    return True

