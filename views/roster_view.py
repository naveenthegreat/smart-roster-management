from coverage_engine import get_overlapping_assignments
import streamlit as st
import pandas as pd
import calendar

from datetime import date

from scheduler import (
    generate_roster,
    get_roster_view,
    get_month_dates,
    is_process_open,
    get_required_staff
)

from validator import validate_roster
from ui_helpers import read_data


COLORS = {
    "W": "background-color: #dcfce7; color: #166534",
    "O": "background-color: #e5e7eb; color: #374151",
    "L": "background-color: #fee2e2; color: #991b1b",
    "H": "background-color: #dbeafe; color: #1e40af",
    "C": "background-color: #fef3c7; color: #92400e",
    "U": "background-color: #f3e8ff; color: #6b21a8"
}


def color_status(value):

    return COLORS.get(value, "")


def show_coverage(year, month):

    roster = get_roster_view(year, month)
    day_columns = [c for c in roster.columns if isinstance(c, int)]

    if roster.empty or not day_columns:
        st.info("No coverage data available for this month.")
        return

    coverage = roster[day_columns].eq("W").sum()
    coverage.index = coverage.index.map(str)
    st.subheader("Daily Staff Coverage")
    st.bar_chart(coverage.rename("Working staff"))


def show():

    st.title("Generate Monthly Roster")

    st.caption(
        "Generate employee schedules and review coverage"
    )

    col1, col2 = st.columns(2)

    year = col1.number_input(
        "Select Year", 2020, 2100,
        date.today().year
    )

    month = col2.selectbox(
        "Select Month",
        range(1, 13),
        index=11,
        format_func=lambda x: calendar.month_name[x]
    )

    st.warning(
        "Generating a roster replaces the existing "
        "schedule for the selected month."
    )

    existing = get_roster_view(year, month)

    confirmed = True

    if not existing.empty:

        confirmed = st.checkbox(
            "I understand that regeneration will replace "
            "the existing roster and manual changes.",
            key=f"regenerate_{year}_{month}"
        )

    if st.button(
        "Generate Roster",
        type="primary",
        disabled=not confirmed
    ):

        with st.spinner("Generating monthly roster..."):

            result = generate_roster(year, month)

        st.success(
            f"Roster generated: {len(result)} records."
        )

    roster = get_roster_view(year, month)

    if roster.empty:

        st.info("No roster generated for this month.")
        return

    conflicts = validate_roster(year, month)

    critical = (
        conflicts["severity"] == "Critical"
    ).sum()

    if critical > 0:

        st.error(
            f"{critical} critical conflicts detected. "
            "This roster requires review before approval."
        )

    else:

        st.success("No critical conflicts detected.")

    employees = read_data("""
        SELECT e.employee_id, e.name, p.pod_name
        FROM employees e
        JOIN pods p ON e.pod_id = p.pod_id
    """)

    roster = roster.merge(
        employees[["employee_id", "pod_name"]],
        on="employee_id",
        how="left"
    )

    view = st.selectbox(
        "Roster View",
        ["Company", "Pod", "Brand", "Process", "Employee"]
    )

    if view == "Pod":

        selected = st.selectbox(
            "Select Pod",
            sorted(employees["pod_name"].unique())
        )

        roster = roster[
            roster["pod_name"] == selected
        ]

    elif view == "Employee":

        options = dict(zip(
            employees["employee_id"], employees["name"]
        ))

        selected = st.selectbox(
            "Select Employee",
            list(options),
            format_func=lambda x: options[x]
        )

        roster = roster[
            roster["employee_id"] == selected
        ]

    elif view in ["Brand", "Process"]:

        mapping = read_data("""
            SELECT a.employee_id,
            b.brand_name, p.process_name

            FROM assignments a

            JOIN brand_processes bp
                ON a.brand_process_id = bp.brand_process_id

            JOIN brands b
                ON bp.brand_id = b.brand_id

            JOIN processes p
                ON bp.process_id = p.process_id
        """)

        column = (
            "brand_name" if view == "Brand"
            else "process_name"
        )

        options = sorted(mapping[column].unique())

        if not options:
            st.info("No assignments available.")
            return

        selected = st.selectbox(
            f"Select {view}", options
        )

        employee_ids = mapping[
            mapping[column] == selected
        ]["employee_id"]

        roster = roster[
            roster["employee_id"].isin(employee_ids)
        ]

    day_columns = [
        c for c in roster.columns
        if isinstance(c, int)
    ]

    roster = roster[
        ["employee_id", "name", "pod_name"] + day_columns
    ]

    roster.columns = roster.columns.map(str)

    day_columns = [str(c) for c in day_columns]

    styled = roster.style.map(
        color_status,
        subset=day_columns
    )

    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True,
        height=500
    )

    st.caption(
        "W: Working | O: Weekly Off | L: Leave | "
        "H: Holiday | C: Comp-off | U: Unavailable"
    )

    st.download_button(
        "Download Roster CSV",
        roster.to_csv(index=False).encode("utf-8"),
        file_name=f"roster_{year}_{month:02d}.csv",
        mime="text/csv"
    )

    st.divider()

    show_coverage(year, month)

def show_coverage(year, month):

    st.subheader("Daily Brand Coverage")

    dates = get_month_dates(year, month)

    selected_date = st.date_input(
        "Coverage Date",
        value=dates[0],
        min_value=dates[0],
        max_value=dates[-1],
        key=f"coverage_{year}_{month}"
    )

    processes = read_data("""
        SELECT bp.*, b.brand_name, p.process_name

        FROM brand_processes bp

        JOIN brands b ON bp.brand_id = b.brand_id

        JOIN processes p ON bp.process_id = p.process_id
    """)

    assignments = read_data("""
        SELECT a.brand_process_id, a.employee_id,
        e.name, r.status

        FROM assignments a

        JOIN employees e
            ON a.employee_id = e.employee_id

        LEFT JOIN roster r
            ON a.employee_id = r.employee_id
            AND r.work_date = ?
    """, (selected_date.isoformat(),))

    holidays = read_data("SELECT holiday_date FROM holidays")

    holiday_dates = set(holidays["holiday_date"])
    assignment_details = read_data(
        "SELECT * FROM assignments"
    )

    roster_lookup = {
        (row["employee_id"], selected_date.isoformat()):
        row["status"]
        for _, row in assignments.iterrows()
    }

    blocked = get_overlapping_assignments(
        [selected_date],
        processes,
        assignment_details,
        roster_lookup,
        holiday_dates
    )

    records = []

    for _, process in processes.iterrows():

        active = is_process_open(
            process, selected_date, holiday_dates
        )

        assigned = assignments[
            assignments["brand_process_id"] ==
            process["brand_process_id"]
        ]

        working = assigned[
            assigned["status"] == "W"
        ].copy()

        working = working[
            [
                (
                    row["employee_id"],
                    process["brand_process_id"],
                    selected_date.isoformat()
                ) not in blocked

                for _, row in working.iterrows()
            ]
        ] if not working.empty else working

        required = (
            get_required_staff(process, selected_date)
            if active else 0
        )

        available = len(working) if active else 0

        if not active:
            status = "Closed"

        elif available >= required:
            status = "Covered"

        else:
            status = "Shortage"

        records.append({
            "Brand": process["brand_name"],
            "Process": process["process_name"],
            "Required": required,
            "Available": available,
            "Shortage": max(0, required - available),
            "Working Employees": (
                ", ".join(working["name"]) if active else "-"
            ),
            "Status": status
        })

    coverage = pd.DataFrame(
        records,
        columns=[
            "Brand", "Process", "Required",
            "Available", "Shortage",
            "Working Employees", "Status"
        ]
    )

    brand = st.selectbox(
        "Filter Coverage by Brand",
        ["All"] + sorted(coverage["Brand"].unique())
    )

    if brand != "All":

        coverage = coverage[
            coverage["Brand"] == brand
        ]

    st.dataframe(
        coverage,
        hide_index=True,
        use_container_width=True
    )

    st.caption(
    "Coverage excludes conflicting shift assignments. "
    "Review Conflict Reports to resolve overlaps."
)