import calendar 
from datetime import date, timedelta
from database import get_connection
import pandas as pd

def load_staffing_rules():

    conn = get_connection()

    try:

        rules = pd.read_sql_query(
            "SELECT * FROM staffing_rules",
            conn
        )

    finally:

        conn.close()

    return {
        (
            row["brand_process_id"],
            row["weekday"]
        ): row["min_staff"]

        for _, row in rules.iterrows()
    }

def get_month_dates(year,month):
    total_days = calendar.monthrange(year, month)[1]
    dates = []
    for day in range(1, total_days + 1):
        current_date = date(year, month, day)
        dates.append(current_date)
    return dates


def fetch_data():

    conn = get_connection()

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

        brand_processes = pd.read_sql_query(
            "SELECT * FROM brand_processes", conn
        )

        assignments = pd.read_sql_query(
            "SELECT * FROM assignments", conn
        )

        return (
            employees,
            leaves,
            holidays,
            brand_processes,
            assignments
        )

    finally:
        conn.close()


def get_employee_status(
    employee,
    current_date,
    leave_lookup,
    holiday_dates
):

    employee_id = employee["employee_id"]

    date_string = current_date.isoformat()

    day_name = current_date.strftime("%A")

    if (employee_id, date_string) in leave_lookup:

        return leave_lookup[
            (employee_id, date_string)
        ]

    if date_string in holiday_dates:

        if employee["holiday_off"] == 1:

            return "H"

    if day_name == employee["weekly_off"]:

        return "O"

    return "W"


def is_process_open(
    process,
    current_date,
    holiday_dates
):

    rule = process["working_rule"]

    is_sunday = current_date.weekday() == 6

    is_holiday = (
        current_date.isoformat() in holiday_dates
    )

    if rule == "ALL_DAYS":
        return True

    elif rule == "NO_HOLIDAYS":
        return not is_holiday

    elif rule == "NO_SUNDAY_HOLIDAYS":
        return not is_sunday and not is_holiday

    else:
        raise ValueError(f"Unknown working rule: {rule}")


def get_required_staff(
    process,
    current_date,
    staffing_rules=None
):

    if staffing_rules is None:
        staffing_rules = load_staffing_rules()

    key = (
        process["brand_process_id"],
        current_date.weekday()
    )

    if key in staffing_rules:

        return int(staffing_rules[key])

    if current_date.weekday() == 6:

        sunday_staff = process["sunday_min_staff"]

        if pd.notna(sunday_staff):

            return int(sunday_staff)

    return int(process["min_staff"])

def adjust_weekly_offs(
    roster,
    dates,
    brand_processes,
    assignments,
    holiday_dates
):

    process_map = {
        p["brand_process_id"]: p
        for _, p in brand_processes.iterrows()
    }

    assigned_employees = (
        assignments.groupby("brand_process_id")
        ["employee_id"].apply(list).to_dict()
    )

    employee_processes = (
        assignments.groupby("employee_id")
        ["brand_process_id"].apply(list).to_dict()
    )

    def shortage(bp_id, day):

        process = process_map[bp_id]

        if not is_process_open(
            process, day, holiday_dates
        ):
            return 0

        required = get_required_staff(process, day)

        available = sum(
            roster.get((emp_id, day)) == "W"
            for emp_id in assigned_employees.get(bp_id, [])
        )

        return max(0, required - available)

    for (emp_id, off_date), status in list(roster.items()):

        if status != "O":
            continue

        processes = employee_processes.get(emp_id, [])

        has_shortage = any(
            shortage(bp_id, off_date) > 0
            for bp_id in processes
        )

        if not has_shortage:
            continue

        week_start = off_date - timedelta(
            days=off_date.weekday()
        )

        for new_date in dates:

            new_week_start = new_date - timedelta(
                days=new_date.weekday()
            )

            if new_week_start != week_start:
                continue

            if roster.get((emp_id, new_date)) != "W":
                continue

            # Measure shortage before changing the off.
            before = {
                bp_id: shortage(bp_id, new_date)
                for bp_id in processes
            }

            # Try swapping the weekly off.
            roster[(emp_id, off_date)] = "W"
            roster[(emp_id, new_date)] = "O"

            safe = all(
                shortage(bp_id, new_date) <= before[bp_id]
                for bp_id in processes
            )

            if safe:
                break

            # Undo the change if it creates a shortage.
            roster[(emp_id, off_date)] = "O"
            roster[(emp_id, new_date)] = "W"

    return roster


def generate_roster(year, month):

    (
        employees,
        leaves,
        holidays,
        brand_processes,
        assignments
    ) = fetch_data()

    dates = get_month_dates(year, month)

    leave_lookup = {
        (row["employee_id"], row["leave_date"]):
        row["leave_type"]
        for _, row in leaves.iterrows()
    }

    holiday_dates = set(holidays["holiday_date"])

    roster = {}

    # Generate initial employee schedules.
    for _, employee in employees.iterrows():

        for current_date in dates:

            status = get_employee_status(
                employee,
                current_date,
                leave_lookup,
                holiday_dates
            )

            roster[
                (employee["employee_id"], current_date)
            ] = status

    # Adjust preferred weekly offs.
    roster = adjust_weekly_offs(
        roster,
        dates,
        brand_processes,
        assignments,
        holiday_dates
    )

    records = [
        (int(emp_id), work_date.isoformat(), status)
        for (emp_id, work_date), status in roster.items()
    ]

    save_roster(year, month, records)

    print("Roster generated successfully!")
    print("Total records:", len(records))

    return pd.DataFrame(
        records,
        columns=[
            "employee_id",
            "work_date",
            "status"
        ]
    )



def save_roster(year, month, records):

    conn = get_connection()

    month_prefix = f"{year:04d}-{month:02d}"

    try:

        cursor = conn.cursor()

        # Remove the previously generated roster
        # for the selected month.
        cursor.execute("""
            DELETE FROM roster
            WHERE work_date LIKE ?
        """, (month_prefix + "%",))

        cursor.executemany("""
            INSERT INTO roster
            (employee_id, work_date, status)
            VALUES (?, ?, ?)
        """, records)

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()





def get_roster_view(year, month):

    conn = get_connection()

    month_prefix = f"{year:04d}-{month:02d}"

    query = """
        SELECT
            e.employee_id,
            e.name,
            r.work_date,
            r.status

        FROM roster r

        JOIN employees e
            ON r.employee_id = e.employee_id

        WHERE r.work_date LIKE ?

        ORDER BY e.employee_id, r.work_date
    """

    try:

        df = pd.read_sql_query(
            query,
            conn,
            params=(month_prefix + "%",)
        )

    finally:

        conn.close()

    if df.empty:
        return df

    df["day"] = pd.to_datetime(
        df["work_date"]
    ).dt.day

    roster_view = df.pivot(
        index=["employee_id", "name"],
        columns="day",
        values="status"
    )

    return roster_view.reset_index()


if __name__ == "__main__":

    year = 2026
    month = 12

    generate_roster(year, month)

    roster_view = get_roster_view(year, month)

    print("\nMONTHLY EMPLOYEE ROSTER\n")

    print(roster_view.to_string(index=False))