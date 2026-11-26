# Smart Roster Management System

Smart Roster Management System is a web application that I developed to manage employee schedules, brand coverage and resource assignments. It helps generate monthly rosters, find scheduling conflicts and understand how changes in an employee's schedule can affect different brands and processes.

## Live Application

https://smart-roster-management-system.streamlit.app/

## Problem Statement

Managing employee schedules manually can be difficult when a company handles multiple brands, processes and teams.

Every employee may have different weekly offs, approved leaves, holidays and work responsibilities. Sometimes, an employee may also be assigned to multiple brands or processes at the same time.

I developed this application to manage all these things in one place. It helps managers generate monthly rosters, check employee availability and identify scheduling problems before finalizing the roster.

## Key Features

- Manage employees, brands, processes and operational pods.
- Set working days and operating rules for different brands.
- Manage single-resource and multi-resource brands.
- Manage employee weekly-off preferences.
- Manage approved leaves, public holidays and compensatory offs.
- Set minimum staffing requirements for different days.
- Automatically generate monthly employee rosters.
- View rosters by company, pod, brand, process and employee.
- Check daily brand and process coverage.
- Detect staffing shortages and overlapping shifts.
- Detect weekly rest violations.
- Manually edit employee schedules.
- Compare conflicts before and after a roster change.
- Download rosters and conflict reports in CSV format.
- Test important application functions using Pytest.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend and scheduling logic |
| Streamlit | Web application interface |
| SQLite | Database storage |
| SQL | Database operations |
| Pandas | Data handling and analysis |
| Plotly | Charts and data visualization |
| Pytest | Testing application functions |
| Git and GitHub | Version control and code management |
| Streamlit Community Cloud | Hosting the application |

## Sample Dataset

I used fictional employee and brand data to build and demonstrate this application.

| Entity | Total Records |
|---|---:|
| Employees | 30 |
| Brands | 25 |
| Operational Pods | 5 |
| Process Types | 4 |
| Brand Processes | 60 |
| Resource Assignments | 66 |
| Single-resource Brands | 20 |
| Multi-resource Brands | 5 |

Around 80% of the brands have a single dedicated employee, while the remaining 20% have multiple employees assigned to them.

The sample data also includes approved leaves, overlapping shifts, compensatory offs and different holiday requirements. These were included to test how the application handles different scheduling problems.

## Application Modules

The application is divided into eight main sections:

1. **Dashboard:** Shows an overview of employees, brands, pods and processes using charts and statistics.
2. **Employees:** Manages employee details and weekly-off preferences.
3. **Brands & Processes:** Manages brands, processes, operating rules and resource assignments.
4. **Pods & Teams:** Displays operational teams, team leaders and team members.
5. **Leave & Holidays:** Manages employee leaves, compensatory offs and public holidays.
6. **Generate Roster:** Generates monthly employee schedules based on the available data and working rules.
7. **Edit Roster:** Allows managers to make changes and check their impact before saving.
8. **Conflict Reports:** Displays scheduling conflicts, their severity and possible solutions.

## Project Structure

    smart-roster-management/
    ├── .streamlit/
    │   └── config.toml
    ├── views/
    │   ├── dashboard.py
    │   ├── employees.py
    │   ├── brands.py
    │   ├── pods.py
    │   ├── availability.py
    │   ├── roster_view.py
    │   ├── edit_roster.py
    │   └── conflicts.py
    ├── tests/
    │   ├── test_scheduler.py
    │   ├── test_validator.py
    │   └── test_editor.py
    ├── app.py
    ├── database.py
    ├── seed_data.py
    ├── scheduler.py
    ├── validator.py
    ├── coverage_engine.py
    ├── roster_editor.py
    ├── ui_helpers.py
    ├── requirements.txt
    ├── .gitignore
    └── README.md

## System Architecture

Instead of writing the entire application in a single Python file, I divided it into different files based on their responsibilities. This made the project easier to understand, manage, test and update.

| File | Responsibility |
|---|---|
| app.py | Starts the application and manages navigation |
| database.py | Creates database tables and manages database connections |
| seed_data.py | Adds fictional sample data |
| scheduler.py | Generates monthly employee rosters |
| validator.py | Checks and identifies scheduling conflicts |
| coverage_engine.py | Detects overlapping employee assignments |
| roster_editor.py | Handles manual roster changes and impact analysis |
| ui_helpers.py | Contains reusable database operations |
| views/ | Contains individual application pages |
| tests/ | Contains automated test cases |

## Local Installation

Follow these steps to run the application on your computer.

### Step 1: Clone the repository

    git clone https://github.com/naveenthegreat/smart-roster-management.git

    cd smart-roster-management

### Step 2: Create a virtual environment

    python -m venv venv

### Step 3: Activate the virtual environment

For Windows PowerShell:

    .\venv\Scripts\Activate.ps1

For Linux or macOS:

    source venv/bin/activate

### Step 4: Install the required libraries

    pip install -r requirements.txt

### Step 5: Run the application

    python -m streamlit run app.py

The application automatically creates the SQLite database and adds the sample data.

Open the following URL in your browser:

http://localhost:8501

No external API keys or environment variables are required to run this project.

## How to Use the Application

1. Open the Dashboard to check the overall workforce information.
2. Review employees, brands, processes and operational pods.
3. Set the operating rules and staffing requirements.
4. Add employee leaves, holidays and availability details.
5. Select a month and year.
6. Click on Generate Roster.
7. Review employee schedules and brand coverage.
8. Open Conflict Reports to check scheduling problems.
9. Use Edit Roster to make changes and understand their impact.
10. Download the roster or conflict report if required.

For demonstration purposes, December 2026 is the recommended month because the sample data includes scheduling scenarios for this month.

## Roster Status Codes

The application uses the following codes to represent employee availability.

| Code | Meaning |
|---|---|
| W | Working |
| O | Weekly Off |
| L | Leave |
| H | Public Holiday |
| C | Compensatory Off |
| U | Unavailable |

## Scheduling Approach

I used a rule-based approach to generate employee rosters.

The scheduler first collects all the required information from the database, including employee details, approved leaves, holidays, weekly-off preferences, brand operating rules and resource assignments.

It first applies mandatory restrictions, such as approved leaves and mandatory holidays. After that, it assigns weekly offs based on employee preferences.

If a weekly off causes a staffing shortage, the scheduler tries to move it to another day within the same week, provided that the change does not create an additional staffing shortage on that day.

Once the roster is generated, the validator checks for staffing shortages, overlapping shifts, availability violations, weekly rest violations and other scheduling problems.

The application does not hide conflicts when it cannot satisfy all the requirements. Instead, it reports them so that the manager can review and resolve them.

## Assessment Questions

### 1. How are employees, brands, processes and pods related?

I used a relational SQLite database to manage the relationships between these entities.

Every employee belongs to an operational pod, and each pod has a team leader.

A brand can have multiple processes. For example, a brand may require customer support, order confirmation or other operational processes.

The `brand_processes` table connects brands with processes and stores their operating rules and staffing requirements.

The `assignments` table connects employees with brand processes using a many-to-many relationship. This means one employee can work for multiple brands or processes, and one brand process can have multiple employees.

There are also separate tables for leaves, holidays, weekday staffing requirements and generated roster records.

### 2. How does the roster generation logic work?

The scheduler first collects the required data from the database and generates all the dates for the selected month.

It then assigns a status to each employee for every day based on approved leaves, holidays, availability and weekly-off preferences.

After that, it checks whether moving a weekly off to another day can improve staffing coverage. I used a greedy approach for this, which means the scheduler tries to make a useful adjustment based on the current situation.

Once the roster is generated, it is saved in the database and checked by the validator.

Approved leaves and mandatory restrictions are given higher priority than employee preferences.

If the scheduler cannot meet all staffing requirements, the remaining conflicts are reported for the manager to review.

### 3. How does the system handle single-resource and multi-resource brands?

The system checks employee coverage separately for each brand process.

For a single-resource brand, if the only assigned employee becomes unavailable, the brand process may have no coverage.

For a multi-resource brand, the system checks how many assigned employees are available and whether that number meets the minimum staffing requirement.

If employees have overlapping assignments, they are not counted as confirmed coverage for the affected processes until the overlap is resolved.

### 4. What happens when the only assigned employee becomes unavailable?

The system checks which brands and processes are handled by that employee.

It then checks whether any other assigned employee is available to handle those responsibilities.

If no employee is available, the application generates a Zero Coverage conflict.

The manager can review the conflict and decide whether to assign a backup employee, change resource assignments or adjust the schedule.

The system does not allow approved leaves or mandatory availability restrictions to be overridden through normal roster editing.

### 5. How are scheduling conflicts and insufficient staffing handled?

I developed a separate validation module to identify scheduling problems.

The system detects the following types of conflicts:

- Zero Coverage
- Insufficient Staffing
- Shift Overlap
- Availability Violation
- Missing Roster
- Multiple Brand Impact
- Weekly Off Preference Changed
- Weekly Rest Violation

These conflicts are divided into two categories:

**Critical:** Problems that require attention before the roster can be approved.

**Warning:** Problems that should be reviewed but may not directly stop operations.

The Conflict Reports page shows the affected date, employee, brand, process, conflict description and a suggested action.

This helps managers understand what caused the problem and how they can resolve it.

### 6. Which decisions are automated and which remain under human control?

I wanted the application to reduce manual work without taking complete control away from the manager.

The system automatically handles:

- Monthly roster generation.
- Weekly-off adjustments.
- Employee coverage calculations.
- Scheduling conflict detection.

The manager remains responsible for:

- Employee and resource assignments.
- Brand operating rules.
- Minimum staffing requirements.
- Employee availability information.
- Manual roster changes.

I also included an impact analysis feature that allows managers to check how a proposed change will affect the roster before saving it.

For example, if a manager changes an employee's status from Working to Unavailable, the system shows whether that change creates any additional conflicts.

This allows the manager to make a decision based on the actual impact of the change.

### 7. How would the system scale if the number of employees and brands doubled?

Since the application is divided into separate modules and uses a relational database, more employees, brands, processes and pods can be added without changing the main application logic.

However, as the amount of data increases, some improvements would be required to maintain good performance.

I would focus on:

- Reducing repeated database queries.
- Loading staffing requirements once during validation.
- Adding database indexes.
- Improving the scheduling algorithm.
- Replacing SQLite with PostgreSQL for better storage and support for multiple users.

For more complex scheduling requirements, I would also consider using a constraint-based optimization algorithm.

### 8. What improvements would be implemented with one additional week?

If I had one more week to work on this project, I would focus on improving the scheduling logic and making the application more suitable for real-world use.

Some improvements I would like to implement are:

- A better roster optimization algorithm to reduce staffing conflicts.
- Automatic backup employee recommendations.
- Fairer distribution of weekly offs.
- More detailed employee rest and availability checks.
- User login and role-based access.
- A history of roster changes.
- Permanent cloud database storage using PostgreSQL.
- Better support for multiple managers using the application at the same time.
- More integration and performance tests.

## Testing

I used Pytest to test the important functions of the application.

The automated tests cover:

- Calendar and monthly date generation.
- Leap year handling.
- Brand operating rules.
- Minimum staffing requirements.
- Staffing shortages.
- Overlapping shifts.
- Weekly rest validation.
- Conflict comparison.

To run the tests, use the following command:

    python -m pytest tests/ -v

I also included manual testing scenarios to check how the application behaves in different situations.

These scenarios include:

- Generating a monthly roster.
- Making a single-resource employee unavailable.
- Checking the impact of changes on multi-resource brands.
- Detecting overlapping assignments.
- Preventing approved leave violations.
- Comparing conflicts before and after a manual roster change.

## Assumptions and Limitations

There are some assumptions and limitations in the current version of the application.

- All employee and brand data used in this project is fictional.
- Shift timings are assumed to start and end on the same day.
- Employee weekly-off preferences may be adjusted to improve staffing coverage.
- The current scheduling algorithm does not guarantee the best possible roster in every situation.
- Employees with overlapping assignments are excluded from confirmed coverage instead of automatically assigning priority to one brand.
- Weekly rest validation currently checks complete weeks within the selected month.
- Manual roster changes may be replaced if the roster is generated again for the same month.
- Some conflict calculations use the number of employees scheduled to work without adjusting for overlapping assignments.
- SQLite database changes may be lost when the deployed application restarts or is redeployed.
- User authentication and permanent change history are not included in the current version.

## Development Approach

I developed this project step by step by dividing it into smaller phases.

I started with the database and sample data, then worked on employee management, brand management, roster generation, conflict detection and manual roster editing.

After developing the main functionality, I worked on the user interface, testing, GitHub integration and deployment.

My main goal was to build an application that not only generates employee schedules but also helps managers understand the problems within those schedules.

I used AI assistance for development guidance, code generation and debugging during the project.

## Author

**Naveen Kumar Sharanappa Nayak**
