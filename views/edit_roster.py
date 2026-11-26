import streamlit as st
import calendar

from datetime import date

from ui_helpers import read_data

from scheduler import get_month_dates

from validator import validate_roster

from roster_editor import (
    get_current_status,
    preview_roster_change,
    update_roster_status
)


STATUS_LABELS = {
    "W": "Working",
    "O": "Weekly Off",
    "L": "Approved Leave",
    "H": "Public Holiday",
    "C": "Compensatory Off",
    "U": "Unavailable"
}


def show_impact(result, year, month, employee_id, selected_date, new_status):

    st.subheader("Roster Impact Preview")
    st.caption(
        f"Employee {employee_id} · {selected_date} · "
        f"{STATUS_LABELS.get(new_status, new_status)}"
    )

    if isinstance(result, dict):
        for label, value in result.items():
            st.write(f"**{str(label).replace('_', ' ').title()}:**", value)
    else:
        st.write(result)


def show():

    st.title("Edit Roster")

    st.caption(
        "Modify employee schedules and preview "
        "the operational impact before saving."
    )

    if "roster_edit_message" in st.session_state:

        st.success(
            st.session_state.pop("roster_edit_message")
        )

    col1, col2 = st.columns(2)

    year = col1.number_input(
        "Year", 2020, 2100,
        date.today().year
    )

    month = col2.selectbox(
        "Month",
        range(1, 13),
        index=11,
        format_func=lambda x: calendar.month_name[x]
    )

    employees = read_data("""
        SELECT DISTINCT e.employee_id, e.name
        FROM employees e

        JOIN roster r
            ON e.employee_id = r.employee_id

        WHERE r.work_date LIKE ?

        ORDER BY e.employee_id
    """, (f"{year:04d}-{month:02d}%",))

    if employees.empty:

        st.info(
            "Generate a roster for this month first."
        )

        return

    options = dict(zip(
        employees["employee_id"],
        employees["name"]
    ))

    employee_id = st.selectbox(
        "Select Employee",
        list(options),
        format_func=lambda x: options[x]
    )

    dates = get_month_dates(year, month)

    selected_date = st.date_input(
        "Select Date",
        value=dates[0],
        min_value=dates[0],
        max_value=dates[-1],
        key=f"edit_date_{year}_{month}"
    )

    current_status = get_current_status(
        employee_id, selected_date
    )

    if current_status is None:

        st.warning("No roster entry found.")
        return

    st.divider()

    st.write(
        "**Current Status:**",
        STATUS_LABELS.get(
            current_status, current_status
        )
    )

    new_status = st.selectbox(
        "New Status",
        list(STATUS_LABELS),
        index=list(STATUS_LABELS).index(current_status),
        format_func=lambda x: STATUS_LABELS[x],
        key=(
            f"new_status_{employee_id}_"
            f"{selected_date}_{current_status}"
        )
    )

    if new_status == current_status:

        st.info("Select a different status to make a change.")
        return

    signature = (
        int(year),
        int(month),
        int(employee_id),
        str(selected_date),
        current_status,
        new_status
    )

    if st.button("Preview Impact", type="primary"):

        st.session_state.pop("roster_preview", None)

        try:

            with st.spinner("Analysing roster impact..."):

                result = preview_roster_change(
                    year,
                    month,
                    employee_id,
                    selected_date,
                    new_status
                )

            st.session_state["roster_preview"] = {
                "signature": signature,
                "result": result
            }

        except ValueError as error:

            st.error(str(error))

    preview = st.session_state.get("roster_preview")

    if preview and preview["signature"] == signature:

        show_impact(
            preview["result"],
            year,
            month,
            employee_id,
            selected_date,
            new_status
        )

def show_impact(
    result, year, month,
    employee_id, selected_date, new_status
):

    st.divider()

    st.subheader("Impact Analysis")

    before = result["before"]
    after = result["after"]

    new_conflicts = result["new_conflicts"]

    resolved = result["resolved_conflicts"]

    before_critical = int(
        (before["severity"] == "Critical").sum()
    )

    after_critical = int(
        (after["severity"] == "Critical").sum()
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Conflicts Before", len(before))

    c2.metric(
        "Conflicts After",
        len(after),
        delta=len(after) - len(before),
        delta_color="inverse"
    )

    c3.metric(
        "Critical Conflicts After",
        after_critical,
        delta=after_critical - before_critical,
        delta_color="inverse"
    )

    st.subheader("New or Changed Conflicts")

    if new_conflicts.empty:

        st.success("No new conflicts detected.")

    else:

        st.dataframe(
            new_conflicts,
            hide_index=True,
            use_container_width=True
        )

    st.subheader("Resolved or Replaced Conflicts")

    if resolved.empty:

        st.info("No existing conflict reports removed.")

    else:

        st.dataframe(
            resolved,
            hide_index=True,
            use_container_width=True
        )

    if after_critical > 0:

        st.warning(
            "The resulting roster contains critical "
            "conflicts and requires further review."
        )

    st.divider()

    confirm = st.checkbox(
        "I have reviewed the impact and confirm this change.",
        key=(
            f"confirm_{employee_id}_{selected_date}_"
            f"{new_status}_{result['current_status']}"
        )
    )

    if st.button(
        "Save Roster Change",
        type="primary",
        disabled=not confirm
    ):

        try:

            fresh = preview_roster_change(
                year, month, employee_id,
                selected_date, new_status
            )

            if (
                not fresh["before"].equals(before)
                or not fresh["after"].equals(after)
                or fresh["current_status"]
                != result["current_status"]
            ):

                st.session_state.pop("roster_preview", None)

                st.warning(
                    "Roster information has changed. "
                    "Preview the impact again."
                )

                return

            update_roster_status(
                employee_id,
                selected_date,
                new_status,
                result["current_status"]
            )

            latest = validate_roster(year, month)

            critical = int(
                (latest["severity"] == "Critical").sum()
            )

            st.session_state["roster_edit_message"] = (
                f"Roster updated successfully. "
                f"Total conflicts: {len(latest)}. "
                f"Critical conflicts: {critical}."
            )

            st.session_state.pop("roster_preview", None)

            st.rerun()

        except Exception as error:

            st.error(str(error))

