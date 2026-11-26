import streamlit as st

from database import create_tables
from seed_data import seed_database

from views import (
    dashboard,
    employees,
    brands,
    pods,
    availability,
    roster_view,
    conflicts,
    edit_roster
)


st.set_page_config(
    page_title="Smart Roster Management",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def initialize_database():

    create_tables()
    seed_database()

    return True


initialize_database()


st.sidebar.title("Smart Roster")

st.sidebar.caption("Workforce Management System")

st.sidebar.divider()


pages = {
    "Dashboard": dashboard.show,
    "Employees": employees.show,
    "Brands & Processes": brands.show,
    "Pods & Teams": pods.show,
    "Leave & Holidays": availability.show,
    "Generate Roster": roster_view.show,
    "Edit Roster": edit_roster.show,
    "Conflict Reports": conflicts.show
}


selected_page = st.sidebar.radio(
    "Navigation",
    list(pages.keys())
)


st.sidebar.divider()

st.sidebar.caption("Smart Roster Management v1.0")



pages[selected_page]()