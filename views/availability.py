import streamlit as st

from ui_helpers import read_data, execute_query


def show():

    st.title("Leave & Holidays")
    st.caption("Manage employee availability")

    leave_tab, holiday_tab = st.tabs([
        "Employee Leaves",
        "Public Holidays"
    ])

    with leave_tab:

        leaves = read_data("""
            SELECT l.leave_id, e.name,
            l.leave_date, l.leave_type, l.reason

            FROM leaves l

            JOIN employees e
                ON l.employee_id = e.employee_id

            ORDER BY l.leave_date
        """)

        st.dataframe(
    leaves.astype({"leave_id": str}),
    use_container_width=True,
    hide_index=True
    )

        employees = read_data(
            "SELECT employee_id, name FROM employees"
        )

        options = dict(zip(
            employees["employee_id"],
            employees["name"]
        ))

        types = {
            "L": "Approved Leave",
            "C": "Compensatory Off",
            "U": "Unavailable"
        }

        if options:

            with st.form("add_leave"):

                employee = st.selectbox(
                    "Employee", list(options),
                    format_func=lambda x: options[x]
                )

                leave_date = st.date_input("Date")

                leave_type = st.selectbox(
                    "Leave Type", list(types),
                    format_func=lambda x: types[x]
                )

                reason = st.text_input("Reason")

                if st.form_submit_button("Save Leave"):

                    execute_query("""
                        INSERT INTO leaves
                        (employee_id, leave_date,
                         leave_type, reason)

                        VALUES (?, ?, ?, ?)

                        ON CONFLICT(employee_id, leave_date)
                        DO UPDATE SET
                            leave_type = excluded.leave_type,
                            reason = excluded.reason
                    """, (
                        int(employee),
                        leave_date.isoformat(),
                        leave_type, reason
                    ))

                    st.rerun()

        if not leaves.empty:

            leave_options = {
                int(row["leave_id"]):
                f"{row['name']} - {row['leave_date']}"

                for _, row in leaves.iterrows()
            }

            selected = st.selectbox(
                "Leave to Remove",
                list(leave_options),
                format_func=lambda x: leave_options[x]
            )

            confirm = st.checkbox("Confirm leave removal")

            if st.button("Remove Leave", disabled=not confirm):

                execute_query(
                    "DELETE FROM leaves WHERE leave_id = ?",
                    (int(selected),)
                )

                st.rerun()

    with holiday_tab:

        holidays = read_data(
            "SELECT * FROM holidays ORDER BY holiday_date"
        )

        st.dataframe(
    holidays.astype({"holiday_id": str}),
    use_container_width=True,
    hide_index=True
    )

        with st.form("add_holiday"):

            holiday_name = st.text_input("Holiday Name")

            holiday_date = st.date_input("Holiday Date")

            if st.form_submit_button("Save Holiday"):

                if not holiday_name.strip():
                    st.error("Enter a holiday name.")

                else:

                    execute_query("""
                        INSERT INTO holidays
                        (holiday_date, holiday_name)
                        VALUES (?, ?)

                        ON CONFLICT(holiday_date)
                        DO UPDATE SET
                            holiday_name = excluded.holiday_name
                    """, (
                        holiday_date.isoformat(),
                        holiday_name.strip()
                    ))

                    st.rerun()

        if not holidays.empty:

            options = {
                int(row["holiday_id"]):
                f"{row['holiday_name']} - {row['holiday_date']}"

                for _, row in holidays.iterrows()
            }

            selected = st.selectbox(
                "Holiday to Remove",
                list(options),
                format_func=lambda x: options[x]
            )

            confirm = st.checkbox("Confirm holiday removal")

            if st.button("Remove Holiday", disabled=not confirm):

                execute_query("""
                    DELETE FROM holidays
                    WHERE holiday_id = ?
                """, (int(selected),))

                st.rerun()

    st.info(
        "Availability changes do not automatically regenerate "
        "existing rosters. Review and validate affected months."
    )