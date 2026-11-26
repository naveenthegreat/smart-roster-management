import streamlit as st

from ui_helpers import read_data, execute_query


DAYS = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
]


def show():

    st.title("Employee Management")
    st.caption("Manage employee details and working preferences")

    employees = read_data("""
        SELECT e.employee_id, e.name,
        p.pod_name, e.weekly_off, e.holiday_off

        FROM employees e

        JOIN pods p ON e.pod_id = p.pod_id

        ORDER BY e.employee_id
    """)

    search = st.text_input("Search employee")

    filtered = employees[
        employees["name"].str.contains(
            search, case=False, regex=False
        )
    ]

    st.dataframe(
    filtered.astype({
        "employee_id": str,
        "holiday_off": str
    }),
    use_container_width=True,
    hide_index=True
    )

    pods = read_data("SELECT * FROM pods")

    pod_options = dict(
        zip(pods["pod_id"], pods["pod_name"])
    )

    if not pod_options:
        st.warning("Create a pod first.")
        return

    add, edit, remove = st.tabs([
        "Add Employee",
        "Edit Employee",
        "Remove Employee"
    ])

    with add:

        with st.form("add_employee"):

            name = st.text_input("Employee Name")

            pod = st.selectbox(
                "Select Pod",
                list(pod_options),
                format_func=lambda x: pod_options[x]
            )

            weekly_off = st.selectbox(
                "Preferred Weekly Off", DAYS
            )

            holiday_off = st.checkbox(
                "Public Holidays Off", value=True
            )

            submitted = st.form_submit_button(
                "Add Employee"
            )

            if submitted:

                if not name.strip():
                    st.error("Enter an employee name.")

                else:
                    execute_query("""
                        INSERT INTO employees
                        (name, pod_id, weekly_off, holiday_off)
                        VALUES (?, ?, ?, ?)
                    """, (
                        name.strip(), int(pod),
                        weekly_off, int(holiday_off)
                    ))

                    st.rerun()

    with edit:

        raw = read_data("SELECT * FROM employees")

        if not raw.empty:

            options = dict(
                zip(raw["employee_id"], raw["name"])
            )

            emp_id = st.selectbox(
                "Select Employee",
                list(options),
                format_func=lambda x: options[x]
            )

            employee = raw[
                raw["employee_id"] == emp_id
            ].iloc[0]

            with st.form(f"edit_employee_{emp_id}"):

                name = st.text_input(
                    "Name", value=employee["name"]
                )

                pod = st.selectbox(
                    "Pod",
                    list(pod_options),
                    index=list(pod_options).index(
                        employee["pod_id"]
                    ),
                    format_func=lambda x: pod_options[x]
                )

                weekly_off = st.selectbox(
                    "Weekly Off", DAYS,
                    index=DAYS.index(employee["weekly_off"])
                )

                holiday_off = st.checkbox(
                    "Public Holidays Off",
                    value=bool(employee["holiday_off"])
                )

                if st.form_submit_button("Save Changes"):

                    if not name.strip():
                        st.error("Name cannot be empty.")

                    else:
                        execute_query("""
                            UPDATE employees
                            SET name = ?, pod_id = ?,
                            weekly_off = ?, holiday_off = ?
                            WHERE employee_id = ?
                        """, (
                            name.strip(), int(pod),
                            weekly_off, int(holiday_off),
                            int(emp_id)
                        ))

                        st.rerun()

    with remove:

        if not employees.empty:

            options = dict(zip(
                employees["employee_id"],
                employees["name"]
            ))

            emp_id = st.selectbox(
                "Employee to Remove",
                list(options),
                format_func=lambda x: options[x]
            )

            st.warning(
                "Employees with assignments, leaves or "
                "roster records cannot be directly removed."
            )

            confirm = st.checkbox("Confirm removal")

            if st.button("Remove Employee", disabled=not confirm):

                try:

                    execute_query("""
                        DELETE FROM employees
                        WHERE employee_id = ?
                    """, (int(emp_id),))

                    st.rerun()

                except Exception:
                    st.error(
                        "Cannot remove employee because "
                        "related database records exist."
                    )