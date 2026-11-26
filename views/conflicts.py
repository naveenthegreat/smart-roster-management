import streamlit as st
import plotly.express as px
import calendar

from datetime import date

from validator import validate_roster
from ui_helpers import read_data


def show():

    st.title("Conflict Reports")

    st.caption(
        "Identify staffing shortages and scheduling problems"
    )

    col1, col2 = st.columns(2)

    year = col1.number_input(
        "Year", 2020, 2100, date.today().year
    )

    month = col2.selectbox(
        "Month",
        range(1, 13),
        index=11,
        format_func=lambda x: calendar.month_name[x]
    )

    existing = read_data("""
        SELECT COUNT(*) AS total
        FROM roster
        WHERE work_date LIKE ?
    """, (f"{year:04d}-{month:02d}%",))

    if existing.iloc[0]["total"] == 0:

        st.info("Generate a roster first.")
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
    c2.metric("Critical", int(critical))
    c3.metric("Warnings", int(warnings))

    if conflicts.empty:

        st.success("No conflicts detected.")
        return

    if critical > 0:

        st.error(
            "Critical scheduling problems require attention."
        )

    summary = (
        conflicts["conflict_type"]
        .value_counts()
        .reset_index()
    )

    summary.columns = ["Conflict Type", "Count"]

    fig = px.bar(
        summary,
        x="Conflict Type",
        y="Count",
        color="Conflict Type"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Filter Conflicts")

    col1, col2 = st.columns(2)

    severity = col1.selectbox(
        "Severity",
        ["All", "Critical", "Warning"]
    )

    conflict_type = col2.selectbox(
        "Conflict Type",
        ["All"] + sorted(
            conflicts["conflict_type"].unique()
        )
    )

    search = st.text_input(
        "Search Brand or Employee"
    )

    filtered = conflicts.copy()

    if severity != "All":

        filtered = filtered[
            filtered["severity"] == severity
        ]

    if conflict_type != "All":

        filtered = filtered[
            filtered["conflict_type"] == conflict_type
        ]

    if search:

        filtered = filtered[
            filtered["brand"].str.contains(
                search, case=False, regex=False
            )
            |
            filtered["employee"].str.contains(
                search, case=False, regex=False
            )
        ]

    st.write(f"Showing {len(filtered)} conflicts")

    st.dataframe(
        filtered,
        hide_index=True,
        use_container_width=True,
        height=450
    )

    st.download_button(
        "Download Conflict Report",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name=f"conflicts_{year}_{month:02d}.csv",
        mime="text/csv"
    )

    st.subheader("Conflict Details")

    if not filtered.empty:

        selected = st.selectbox(
            "Select Conflict",
            filtered.index.tolist(),
            format_func=lambda x: (
                f"{filtered.loc[x, 'date']} | "
                f"{filtered.loc[x, 'conflict_type']} | "
                f"{filtered.loc[x, 'brand']}"
            )
        )

        conflict = filtered.loc[selected]

        st.write("**Employee:**", conflict["employee"])

        st.write("**Process:**", conflict["process"])

        st.write("**Description:**", conflict["description"])

        st.info(
            f"Suggested Action: {conflict['suggestion']}"
        )