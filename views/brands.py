import streamlit as st
from datetime import time

from ui_helpers import read_data, execute_query


RULES = {
    "ALL_DAYS": "Every Day",
    "NO_HOLIDAYS": "Every Day Except Holidays",
    "NO_SUNDAY_HOLIDAYS": "Sundays and Holidays Off"
}


def manage_catalog(table, id_column, name_column, label):

    data = read_data(f"SELECT * FROM {table}")

    st.dataframe(
    data.astype({id_column: str}),
    use_container_width=True,
    hide_index=True
    )

    with st.form(f"add_{table}"):

        name = st.text_input(f"New {label} Name")

        if st.form_submit_button(f"Add {label}"):

            if not name.strip():
                st.error("Enter a name.")

            else:
                try:
                    execute_query(
                        f"INSERT INTO {table} "
                        f"({name_column}) VALUES (?)",
                        (name.strip(),)
                    )

                    st.rerun()

                except Exception:
                    st.error("Name already exists or is invalid.")

    if not data.empty:

        options = dict(zip(
            data[id_column], data[name_column]
        ))

        selected = st.selectbox(
            f"Select {label}",
            list(options),
            format_func=lambda x: options[x],
            key=f"select_{table}"
        )

        with st.form(f"edit_{table}_{selected}"):

            name = st.text_input(
                "Updated Name", value=options[selected]
            )

            if st.form_submit_button("Save Name"):

                if name.strip():

                    try:
                        execute_query(
                            f"UPDATE {table} "
                            f"SET {name_column} = ? "
                            f"WHERE {id_column} = ?",
                            (name.strip(), int(selected))
                        )

                        st.rerun()

                    except Exception:
                        st.error("Unable to update name.")

                else:
                    st.error("Enter a valid name.")

        confirm = st.checkbox(
            f"Confirm {label.lower()} removal",
            key=f"confirm_{table}"
        )

        if st.button(
            f"Remove {label}",
            disabled=not confirm
        ):

            try:
                execute_query(
                    f"DELETE FROM {table} "
                    f"WHERE {id_column} = ?",
                    (int(selected),)
                )

                st.rerun()

            except Exception:
                st.error("Remove related records first.")


def manage_rules():

    brands = read_data("SELECT * FROM brands")
    processes = read_data("SELECT * FROM processes")

    brand_options = dict(zip(
        brands["brand_id"], brands["brand_name"]
    ))

    process_options = dict(zip(
        processes["process_id"], processes["process_name"]
    ))

    existing = read_data("""
        SELECT bp.*, b.brand_name, p.process_name

        FROM brand_processes bp

        JOIN brands b
            ON bp.brand_id = b.brand_id

        JOIN processes p
            ON bp.process_id = p.process_id
    """)

    st.dataframe(
    existing.astype({"brand_process_id": str}),
    use_container_width=True,
    hide_index=True
    )

    if not brand_options or not process_options:
        st.warning("Create brands and processes first.")
        return

    with st.form("configure_rule"):

        brand = st.selectbox(
            "Brand", list(brand_options),
            format_func=lambda x: brand_options[x]
        )

        process = st.selectbox(
            "Process", list(process_options),
            format_func=lambda x: process_options[x]
        )

        rule = st.selectbox(
            "Operating Rule", list(RULES),
            format_func=lambda x: RULES[x]
        )

        minimum = st.number_input(
            "Minimum Required Employees",
            min_value=1, value=1, step=1
        )

        sunday = st.number_input(
            "Sunday Minimum Staff (0 = Use Default)",
            min_value=0, value=0, step=1
        )

        if st.form_submit_button("Save Operating Rule"):

            execute_query("""
                INSERT INTO brand_processes
                (brand_id, process_id, working_rule,
                 min_staff, sunday_min_staff)

                VALUES (?, ?, ?, ?, ?)

                ON CONFLICT(brand_id, process_id)
                DO UPDATE SET
                    working_rule = excluded.working_rule,
                    min_staff = excluded.min_staff,
                    sunday_min_staff = excluded.sunday_min_staff
            """, (
                int(brand), int(process), rule,
                int(minimum),
                int(sunday) if sunday > 0 else None
            ))

            st.rerun()

    if not existing.empty:

        options = {
            int(row["brand_process_id"]):
            f"{row['brand_name']} - {row['process_name']}"

            for _, row in existing.iterrows()
        }

        selected = st.selectbox(
            "Operating Rule to Remove",
            list(options),
            format_func=lambda x: options[x]
        )

        confirm = st.checkbox("Confirm rule removal")

        if st.button("Remove Rule", disabled=not confirm):

            try:
                execute_query("""
                    DELETE FROM brand_processes
                    WHERE brand_process_id = ?
                """, (int(selected),))

                st.rerun()

            except Exception:
                st.error("Remove resource assignments first.")

def manage_assignments():

    employees = read_data("SELECT * FROM employees")

    processes = read_data("""
        SELECT bp.brand_process_id,
        b.brand_name, p.process_name

        FROM brand_processes bp

        JOIN brands b ON bp.brand_id = b.brand_id

        JOIN processes p ON bp.process_id = p.process_id
    """)

    assignments = read_data("""
        SELECT a.assignment_id, e.name,
        b.brand_name, p.process_name,
        a.start_time, a.end_time

        FROM assignments a

        JOIN employees e
            ON a.employee_id = e.employee_id

        JOIN brand_processes bp
            ON a.brand_process_id = bp.brand_process_id

        JOIN brands b
            ON bp.brand_id = b.brand_id

        JOIN processes p
            ON bp.process_id = p.process_id
    """)

    st.dataframe(
    assignments.astype({"assignment_id": str}),
    use_container_width=True,
    hide_index=True
    )

    employee_options = dict(zip(
        employees["employee_id"], employees["name"]
    ))

    process_options = {
        int(row["brand_process_id"]):
        f"{row['brand_name']} - {row['process_name']}"

        for _, row in processes.iterrows()
    }

    if not employee_options or not process_options:
        st.warning("Create employees and brand processes first.")
        return

    with st.form("resource_assignment"):

        employee = st.selectbox(
            "Employee",
            list(employee_options),
            format_func=lambda x: employee_options[x]
        )

        process = st.selectbox(
            "Brand and Process",
            list(process_options),
            format_func=lambda x: process_options[x]
        )

        start = st.time_input("Start Time", time(9, 0))
        end = st.time_input("End Time", time(18, 0))

        if st.form_submit_button("Save Assignment"):

            if start >= end:
                st.error("End time must be after start time.")

            else:

                execute_query("""
                    INSERT INTO assignments
                    (employee_id, brand_process_id,
                     start_time, end_time)

                    VALUES (?, ?, ?, ?)

                    ON CONFLICT(employee_id, brand_process_id)
                    DO UPDATE SET
                        start_time = excluded.start_time,
                        end_time = excluded.end_time
                """, (
                    int(employee), int(process),
                    start.strftime("%H:%M"),
                    end.strftime("%H:%M")
                ))

                st.rerun()

    if not assignments.empty:

        options = {
            int(row["assignment_id"]):
            f"{row['name']} - {row['brand_name']} - "
            f"{row['process_name']}"

            for _, row in assignments.iterrows()
        }

        selected = st.selectbox(
            "Assignment to Remove",
            list(options),
            format_func=lambda x: options[x]
        )

        confirm = st.checkbox("Confirm assignment removal")

        if st.button("Remove Assignment", disabled=not confirm):

            execute_query("""
                DELETE FROM assignments
                WHERE assignment_id = ?
            """, (int(selected),))

            st.rerun()

def manage_weekday_staffing():

    st.subheader("Weekday Staffing Requirements")

    data = read_data("""
        SELECT bp.brand_process_id,
        b.brand_name, p.process_name

        FROM brand_processes bp

        JOIN brands b
            ON bp.brand_id = b.brand_id

        JOIN processes p
            ON bp.process_id = p.process_id
    """)

    if data.empty:
        st.info("Configure a brand process first.")
        return

    options = {
        int(row["brand_process_id"]):
        f"{row['brand_name']} - {row['process_name']}"

        for _, row in data.iterrows()
    }

    days = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    with st.form("weekday_staffing"):

        process = st.selectbox(
            "Brand Process",
            list(options),
            format_func=lambda x: options[x]
        )

        weekday = st.selectbox(
            "Weekday",
            range(7),
            format_func=lambda x: days[x]
        )

        minimum = st.number_input(
            "Required Employees",
            min_value=1,
            value=1
        )

        if st.form_submit_button("Save Staffing Rule"):

            execute_query("""
                INSERT INTO staffing_rules
                (brand_process_id, weekday, min_staff)

                VALUES (?, ?, ?)

                ON CONFLICT(brand_process_id, weekday)
                DO UPDATE SET
                    min_staff = excluded.min_staff
            """, (
                int(process),
                int(weekday),
                int(minimum)
            ))

            st.rerun()

    rules = read_data("SELECT * FROM staffing_rules")

    if not rules.empty:

        display = rules.copy()

        display["Brand Process"] = (
            display["brand_process_id"].map(options)
        )

        display["Day"] = display["weekday"].map(
            dict(enumerate(days))
        )

        st.dataframe(
            display[
                ["rule_id", "Brand Process", "Day", "min_staff"]
            ],
            hide_index=True
        )

        selected = st.selectbox(
            "Staffing Rule to Remove",
            rules["rule_id"].tolist()
        )

        if st.button("Remove Staffing Rule"):

            execute_query(
                "DELETE FROM staffing_rules WHERE rule_id = ?",
                (int(selected),)
            )

            st.rerun()

def show():

    st.title("Brands & Processes")

    st.caption(
        "Configure clients, operating rules and resources"
    )

    t1, t2, t3, t4 = st.tabs([
        "Brands",
        "Processes",
        "Operating Rules",
        "Resource Assignments"
    ])

    with t1:
        manage_catalog(
            "brands", "brand_id",
            "brand_name", "Brand"
        )

    with t2:
        manage_catalog(
            "processes", "process_id",
            "process_name", "Process"
        )

    with t3:
        manage_rules()

        st.divider()

        manage_weekday_staffing()

    with t4:
        manage_assignments()