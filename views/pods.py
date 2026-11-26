import streamlit as st

from ui_helpers import read_data, execute_query


def show():

    st.title("Pods & Teams")
    st.caption("Manage operational teams and pod leaders")

    pods = read_data("""
        SELECT p.pod_id, p.pod_name, p.pod_lead,
        COUNT(e.employee_id) AS team_size

        FROM pods p

        LEFT JOIN employees e
            ON p.pod_id = e.pod_id

        GROUP BY p.pod_id, p.pod_name, p.pod_lead
    """)

    st.dataframe(
    pods.astype({
        "pod_id": str,
        "team_size": str
    }),
    use_container_width=True,
    hide_index=True
    )

    with st.expander("Add New Pod"):

        with st.form("add_pod"):

            name = st.text_input("Pod Name")
            lead = st.text_input("Pod Leader")

            if st.form_submit_button("Create Pod"):

                if not name.strip() or not lead.strip():
                    st.error("Complete all fields.")

                else:
                    try:

                        execute_query("""
                            INSERT INTO pods
                            (pod_name, pod_lead)
                            VALUES (?, ?)
                        """, (name.strip(), lead.strip()))

                        st.rerun()

                    except Exception:
                        st.error("Pod could not be created.")

    if not pods.empty:

        options = dict(zip(
            pods["pod_id"], pods["pod_name"]
        ))

        selected = st.selectbox(
            "Select Pod",
            list(options),
            format_func=lambda x: options[x]
        )

        pod = pods[
            pods["pod_id"] == selected
        ].iloc[0]

        with st.form(f"edit_pod_{selected}"):

            name = st.text_input(
                "Pod Name", value=pod["pod_name"]
            )

            lead = st.text_input(
                "Pod Leader", value=pod["pod_lead"]
            )

            if st.form_submit_button("Update Pod"):

                if name.strip() and lead.strip():

                    try:
                        execute_query("""
                            UPDATE pods
                            SET pod_name = ?, pod_lead = ?
                            WHERE pod_id = ?
                        """, (
                            name.strip(), lead.strip(),
                            int(selected)
                        ))

                        st.rerun()

                    except Exception:
                        st.error("Unable to update pod.")

                else:
                    st.error("Complete all fields.")

        st.subheader("Team Members")

        members = read_data("""
            SELECT employee_id, name, weekly_off
            FROM employees
            WHERE pod_id = ?
        """, (int(selected),))

        st.dataframe(
    members.astype({"employee_id": str}),
    use_container_width=True,
    hide_index=True
)

        confirm = st.checkbox("Confirm pod removal")

        if st.button("Remove Pod", disabled=not confirm):

            try:
                execute_query(
                    "DELETE FROM pods WHERE pod_id = ?",
                    (int(selected),)
                )

                st.rerun()

            except Exception:
                st.error(
                    "Move employees to another pod first."
                )