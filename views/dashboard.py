import streamlit as st
import plotly.express as px
from datetime import date

from ui_helpers import read_data, get_count
from validator import validate_roster


def show():

    st.title("Dashboard")
    st.caption("Workforce and operational overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Employees", get_count("employees"))
    col2.metric("Total Brands", get_count("brands"))
    col3.metric("Operational Pods", get_count("pods"))
    col4.metric("Total Processes", get_count("processes"))

    st.divider()

    brand_data = read_data("""
        SELECT b.brand_name,
        COUNT(DISTINCT a.employee_id) AS employees

        FROM brands b

        LEFT JOIN brand_processes bp
            ON b.brand_id = bp.brand_id

        LEFT JOIN assignments a
            ON bp.brand_process_id = a.brand_process_id

        GROUP BY b.brand_id, b.brand_name
    """)

    brand_data["resource_type"] = (
        brand_data["employees"].apply(
            lambda x: "Single Resource" if x == 1
            else "Multi Resource" if x > 1
            else "Unassigned"
        )
    )

    distribution = (
        brand_data["resource_type"]
        .value_counts()
        .reset_index()
    )

    distribution.columns = ["Type", "Count"]

    left, right = st.columns(2)

    with left:

        st.subheader("Brand Resource Distribution")

        fig = px.pie(
            distribution,
            names="Type",
            values="Count",
            hole=0.5
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:

        st.subheader("Employees by Pod")

        pod_data = read_data("""
            SELECT p.pod_name,
            COUNT(e.employee_id) AS employees

            FROM pods p

            LEFT JOIN employees e
                ON p.pod_id = e.pod_id

            GROUP BY p.pod_id, p.pod_name
        """)

        fig = px.bar(
            pod_data,
            x="pod_name",
            y="employees",
            color="pod_name"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Monthly Conflict Overview")

    col1, col2 = st.columns(2)

    year = col1.number_input(
        "Year", 2020, 2100, date.today().year
    )

    month = col2.selectbox(
        "Month",
        range(1, 13),
        index=11
    )

    existing = read_data("""
        SELECT COUNT(*) AS total
        FROM roster
        WHERE work_date LIKE ?
    """, (f"{year:04d}-{month:02d}%",))

    if existing.iloc[0]["total"] == 0:

        st.info("Generate a roster for this month first.")
        return

    conflicts = validate_roster(year, month)

    critical = (
        conflicts["severity"] == "Critical"
    ).sum()

    warnings = (
        conflicts["severity"] == "Warning"
    ).sum()

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Conflicts", len(conflicts))
    c2.metric("Critical Conflicts", int(critical))
    c3.metric("Warnings", int(warnings))

    if not conflicts.empty:

        summary = (
            conflicts["conflict_type"]
            .value_counts()
            .reset_index()
        )

        summary.columns = ["Conflict", "Count"]

        fig = px.bar(
            summary,
            x="Count",
            y="Conflict",
            orientation="h",
            color="Conflict"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.success("No conflicts detected.")