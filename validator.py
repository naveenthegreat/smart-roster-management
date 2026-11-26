from datetime import timedelta

from coverage_engine import get_overlapping_assignments

import pandas as pd

from itertools import combinations

from database import get_connection

from scheduler import (
    get_month_dates,
    is_process_open,
    get_required_staff
)


def fetch_validation_data(year, month):

    conn = get_connection()

    month_prefix = f"{year:04d}-{month:02d}"

    try:

        employees = pd.read_sql_query(
            "SELECT * FROM employees", conn
        )

        leaves = pd.read_sql_query(
            "SELECT * FROM leaves", conn
        )

        holidays = pd.read_sql_query(
            "SELECT * FROM holidays", conn
        )

        processes = pd.read_sql_query("""
            SELECT
                bp.*,
                b.brand_name,
                p.process_name
            FROM brand_processes bp

            JOIN brands b
                ON bp.brand_id = b.brand_id

            JOIN processes p
                ON bp.process_id = p.process_id
        """, conn)

        assignments = pd.read_sql_query(
            "SELECT * FROM assignments", conn
        )

        roster = pd.read_sql_query("""
            SELECT * FROM roster
            WHERE work_date LIKE ?
        """, conn, params=(month_prefix + "%",))

        return (
            employees,
            leaves,
            holidays,
            processes,
            assignments,
            roster
        )

    finally:
        conn.close()


def create_conflict(
    work_date,
    conflict_type,
    severity,
    brand,
    process,
    employee,
    description,
    suggestion
):

    return {
        "date": str(work_date),
        "conflict_type": conflict_type,
        "severity": severity,
        "brand": brand,
        "process": process,
        "employee": employee,
        "description": description,
        "suggestion": suggestion
    }


def check_staffing(
    dates,
    processes,
    assignments,
    roster_lookup,
    holiday_dates,
    employee_names
):

    conflicts = []

    blocked = get_overlapping_assignments(
        dates,
        processes,
        assignments,
        roster_lookup,
        holiday_dates
    )
    process_map = {
        row["brand_process_id"]: row
        for _, row in processes.iterrows()
    }

    for emp_id, group in assignments.groupby("employee_id"):
        employee_assignments = group.to_dict("records")

        for current_date in dates:
            date_string = current_date.isoformat()
            if roster_lookup.get((emp_id, date_string)) != "W":
                continue

            active_assignments = [
                assignment
                for assignment in employee_assignments
                if is_process_open(
                    process_map[assignment["brand_process_id"]],
                    current_date,
                    holiday_dates
                )
            ]

            for first, second in combinations(active_assignments, 2):
                if (
                    first["start_time"] < second["end_time"]
                    and second["start_time"] < first["end_time"]
                ):
                    blocked.add(
                        (emp_id, first["brand_process_id"], date_string)
                    )
                    blocked.add(
                        (emp_id, second["brand_process_id"], date_string)
                    )

    assigned_employees = (
        assignments.groupby("brand_process_id")
        ["employee_id"].apply(list).to_dict()
    )

    for _, process in processes.iterrows():

        bp_id = process["brand_process_id"]

        employee_ids = assigned_employees.get(
            bp_id, []
        )

        for current_date in dates:

            # Skip closed brand processes.
            if not is_process_open(
                process,
                current_date,
                holiday_dates
            ):
                continue

            required = get_required_staff(
                process, current_date
            )

            available = []
            unavailable = []

            for emp_id in employee_ids:
                status = roster_lookup.get(
                    (emp_id, current_date.isoformat()),
                    "MISSING"
                )

                if status == "W":
                    if (emp_id, bp_id, current_date.isoformat()) in blocked:
                        unavailable.append(
                            f"{employee_names[emp_id]} (Shift Overlap)"
                        )
                    else:
                        available.append(emp_id)
                else:
                    unavailable.append(
                        f"{employee_names[emp_id]} ({status})"
                    )

            available_count = len(available)

            if available_count < required:

                if available_count == 0:
                    conflict_type = "Zero Coverage"

                else:
                    conflict_type = "Insufficient Staffing"

                shortage = required - available_count

                description = (
                    f"Required: {required}, "
                    f"Available: {available_count}, "
                    f"Shortage: {shortage}. "
                    f"Unavailable: "
                    f"{', '.join(unavailable) or 'No employees assigned'}"
                )

                conflicts.append(
                    create_conflict(
                        current_date,
                        conflict_type,
                        "Critical",
                        process["brand_name"],
                        process["process_name"],
                        ", ".join(unavailable),
                        description,
                        "Assign an available backup employee."
                    )
                )

    return conflicts


def check_shift_overlaps(
    dates,
    processes,
    assignments,
    roster_lookup,
    holiday_dates,
    employee_names
):

    conflicts = []

    process_map = {
        row["brand_process_id"]: row
        for _, row in processes.iterrows()
    }

    for emp_id, group in assignments.groupby(
        "employee_id"
    ):

        employee_assignments = group.to_dict(
            "records"
        )

        for current_date in dates:

            status = roster_lookup.get(
                (emp_id, current_date.isoformat())
            )

            if status != "W":
                continue

            active_assignments = []

            for assignment in employee_assignments:

                process = process_map[
                    assignment["brand_process_id"]
                ]

                if is_process_open(
                    process,
                    current_date,
                    holiday_dates
                ):

                    active_assignments.append(
                        assignment
                    )

            for first, second in combinations(
                active_assignments, 2
            ):

                if (
                    first["start_time"] < second["end_time"]
                    and
                    second["start_time"] < first["end_time"]
                ):

                    p1 = process_map[
                        first["brand_process_id"]
                    ]

                    p2 = process_map[
                        second["brand_process_id"]
                    ]

                    description = (
                        f"{employee_names[emp_id]} has "
                        f"overlapping assignments: "
                        f"{p1['brand_name']} "
                        f"({first['start_time']}-"
                        f"{first['end_time']}) and "
                        f"{p2['brand_name']} "
                        f"({second['start_time']}-"
                        f"{second['end_time']})."
                    )

                    conflicts.append(
                        create_conflict(
                            current_date,
                            "Shift Overlap",
                            "Critical",
                            f"{p1['brand_name']}, {p2['brand_name']}",
                            f"{p1['process_name']}, {p2['process_name']}",
                            employee_names[emp_id],
                            description,
                            "Change shift timings or reassign a responsibility."
                        )
                    )

    return conflicts


def check_availability(
    dates,
    employees,
    leaves,
    holiday_dates,
    roster_lookup
):

    conflicts = []

    leave_lookup = {
        (row["employee_id"], row["leave_date"]):
        row["leave_type"]
        for _, row in leaves.iterrows()
    }

    for _, employee in employees.iterrows():

        emp_id = employee["employee_id"]
        name = employee["name"]

        for current_date in dates:

            date_string = current_date.isoformat()

            key = (emp_id, date_string)

            status = roster_lookup.get(key)

            if status is None:

                conflicts.append(
                    create_conflict(
                        current_date,
                        "Missing Roster",
                        "Critical",
                        "-",
                        "-",
                        name,
                        "No roster entry exists for this employee.",
                        "Generate or complete the roster."
                    )
                )

                continue

            if status != "W":
                continue

            reason = None

            if key in leave_lookup:

                reason = (
                    "Employee is scheduled during "
                    "approved leave, comp-off or unavailability."
                )

            elif (
                date_string in holiday_dates
                and employee["holiday_off"] == 1
            ):

                reason = (
                    "Employee is scheduled during "
                    "a mandatory holiday off."
                )

            if reason:

                conflicts.append(
                    create_conflict(
                        current_date,
                        "Availability Violation",
                        "Critical",
                        "-",
                        "-",
                        name,
                        reason,
                        "Restore the employee's unavailable status."
                    )
                )

    return conflicts


def check_multiple_brand_impact(
    dates,
    processes,
    assignments,
    roster_lookup,
    holiday_dates,
    employee_names
):

    conflicts = []

    process_map = {
        row["brand_process_id"]: row
        for _, row in processes.iterrows()
    }

    assigned_employees = (
        assignments.groupby("brand_process_id")
        ["employee_id"].apply(list).to_dict()
    )

    for emp_id, group in assignments.groupby(
        "employee_id"
    ):

        for current_date in dates:

            date_string = current_date.isoformat()

            status = roster_lookup.get(
                (emp_id, date_string)
            )

            if status is None or status == "W":
                continue

            affected_brands = set()

            for bp_id in group["brand_process_id"]:

                process = process_map[bp_id]

                if not is_process_open(
                    process,
                    current_date,
                    holiday_dates
                ):
                    continue

                required = get_required_staff(
                    process, current_date
                )

                available = sum(
                    roster_lookup.get(
                        (other_id, date_string)
                    ) == "W"
                    for other_id in assigned_employees.get(
                        bp_id, []
                    )
                )

                if available < required:

                    affected_brands.add(
                        process["brand_name"]
                    )

            if len(affected_brands) > 1:

                brand_list = ", ".join(
                    sorted(affected_brands)
                )

                conflicts.append(
                    create_conflict(
                        current_date,
                        "Multiple Brand Impact",
                        "Warning",
                        brand_list,
                        "-",
                        employee_names[emp_id],
                        f"Employee absence contributes to shortages "
                        f"across {len(affected_brands)} brands.",
                        "Review backup coverage across affected brands."
                    )
                )

    return conflicts


def check_preferences(
    dates,
    employees,
    roster_lookup
):

    conflicts = []

    for _, employee in employees.iterrows():

        emp_id = employee["employee_id"]

        preferred_day = employee["weekly_off"]

        for current_date in dates:

            status = roster_lookup.get(
                (emp_id, current_date.isoformat())
            )

            actual_day = current_date.strftime("%A")

            if (
                status == "O"
                and actual_day != preferred_day
            ):

                conflicts.append(
                    create_conflict(
                        current_date,
                        "Weekly Off Preference Changed",
                        "Warning",
                        "-",
                        "-",
                        employee["name"],
                        f"Preferred weekly off: {preferred_day}. "
                        f"Scheduled weekly off: {actual_day}.",
                        "Review the adjusted weekly off with the employee."
                    )
                )

    return conflicts

def check_weekly_rest(
    dates,
    employees,
    roster_lookup
):

    conflicts = []

    weeks = {}

    for current_date in dates:

        week_start = current_date - timedelta(
            days=current_date.weekday()
        )

        weeks.setdefault(
            week_start, []
        ).append(current_date)

    for _, employee in employees.iterrows():

        emp_id = employee["employee_id"]

        for week_start, week_dates in weeks.items():

            if len(week_dates) != 7:
                continue

            statuses = [
                roster_lookup.get(
                    (emp_id, day.isoformat())
                )
                for day in week_dates
            ]

            if all(status == "W" for status in statuses):

                conflicts.append(
                    create_conflict(
                        week_start,
                        "Weekly Rest Violation",
                        "Critical",
                        "-",
                        "-",
                        employee["name"],
                        "Employee is scheduled to work "
                        "all seven days of the week.",
                        "Provide a rest day and arrange "
                        "backup coverage if required."
                    )
                )

    return conflicts

def validate_roster(year, month, overrides=None):

    (
        employees,
        leaves,
        holidays,
        processes,
        assignments,
        roster
    ) = fetch_validation_data(year, month)

    dates = get_month_dates(year, month)

    holiday_dates = set(
        holidays["holiday_date"]
    )

    employee_names = dict(
        zip(
            employees["employee_id"],
            employees["name"]
        )
    )

    roster_lookup = {
        (row["employee_id"], row["work_date"]): row["status"]
        for _, row in roster.iterrows()
    }

    if overrides:
        roster_lookup.update(overrides)

    conflicts = []

    conflicts.extend(
        check_staffing(
            dates,
            processes,
            assignments,
            roster_lookup,
            holiday_dates,
            employee_names
        )
    )

    conflicts.extend(
        check_shift_overlaps(
            dates,
            processes,
            assignments,
            roster_lookup,
            holiday_dates,
            employee_names
        )
    )

    conflicts.extend(
        check_availability(
            dates,
            employees,
            leaves,
            holiday_dates,
            roster_lookup
        )
    )

    conflicts.extend(
        check_multiple_brand_impact(
            dates,
            processes,
            assignments,
            roster_lookup,
            holiday_dates,
            employee_names
        )
    )

    conflicts.extend(
        check_preferences(
            dates,
            employees,
            roster_lookup
        )
    )

    conflicts.extend(
    check_weekly_rest(
        dates,
        employees,
        roster_lookup
    )
)

    columns = [
        "date",
        "conflict_type",
        "severity",
        "brand",
        "process",
        "employee",
        "description",
        "suggestion"
    ]

    df = pd.DataFrame(
        conflicts,
        columns=columns
    )

    if not df.empty:

        df = df.sort_values(
            by=["severity", "date"]
        ).reset_index(drop=True)

    return df


if __name__ == "__main__":

    year = 2026
    month = 12

    conflicts = validate_roster(year, month)

    print("\nROSTER VALIDATION COMPLETED")

    print("-" * 50)

    print("Total conflicts:", len(conflicts))

    critical = (
        conflicts["severity"] == "Critical"
    ).sum()

    warnings = (
        conflicts["severity"] == "Warning"
    ).sum()

    print("Critical conflicts:", critical)
    print("Warnings:", warnings)

    if conflicts.empty:

        print("\nNo conflicts detected.")

    else:

        print("\nCONFLICT SUMMARY\n")

        print(
            conflicts["conflict_type"].value_counts()
        )

        print("\nDETAILED CONFLICT REPORT\n")

        print(
            conflicts[
                [
                    "date",
                    "conflict_type",
                    "severity",
                    "brand",
                    "employee"
                ]
            ].head(15).to_string(index=False)
        )