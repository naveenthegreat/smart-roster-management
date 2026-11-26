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

Follow these commands to run the application locally using Windows PowerShell.

```powershell
git clone https://github.com/naveenthegreat/smart-roster-management.git
cd smart-roster-management

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

python -m streamlit run app.py
```

The application automatically creates the database and loads the sample data.

Open `http://localhost:8501` in your browser.

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

The main problem in generating a roster is managing employee availability and meeting the staffing requirements of different brands. Every employee has different weekly offs, leaves and work responsibilities.

To solve this problem, I used a rule-based scheduling approach. The scheduler first collects the required data from the database and gives priority to approved leaves and mandatory holidays. After that, it assigns weekly offs based on employee preferences.

If a weekly off causes a staffing shortage, the scheduler tries to move it to another day within the same week without creating another shortage. Once the roster is generated, the validator checks for conflicts and reports them to the manager.

## Assessment Questions

### 1. How are employees, brands, processes and pods related?

In this project, one employee can work for multiple brands and one brand can have multiple processes. To manage these relationships, I used SQLite as a relational database.

Every employee belongs to a pod and each pod has a team leader. The `brand_processes` table connects brands with their processes and stores their operating rules and staffing requirements.

I used the `assignments` table to connect employees with brand processes through a many-to-many relationship. This means multiple employees can work on the same process and one employee can also handle multiple processes.

There are separate tables for leaves, holidays, staffing requirements and roster records.

### 2. How does the roster generation logic work?

Before generating a roster, we need to know which employees are available and how many employees are required for each process.

First, the scheduler collects the required data from the database and generates the dates for the selected month. Then it assigns a daily status to each employee based on their leaves, holidays and weekly-off preferences.

To reduce staffing shortages, I used a greedy approach where the scheduler tries to move weekly offs to another suitable day. It also checks whether this change creates another staffing shortage.

After this, the generated roster is stored in the database and checked by the validator. If there are any remaining conflicts, they are displayed to the manager.

### 3. How does the system handle single-resource and multi-resource brands?

A single-resource brand depends on one employee, whereas a multi-resource brand has multiple employees assigned to it.

If an employee is unavailable, the system checks whether the available employees can meet the minimum staffing requirement for each process. Employees with overlapping assignments are not counted as confirmed coverage for the affected processes.

### 4. What happens when the only assigned employee becomes unavailable?

In this situation, the system checks whether any other assigned employee is available to handle the process.

If no employee is available, it generates a Zero Coverage conflict and marks it as critical. The manager can then assign a backup employee or change the resource assignments without overriding approved leaves or mandatory restrictions.

### 5. How are scheduling conflicts and insufficient staffing handled?

Even after generating a roster, there can be some problems like staffing shortages, overlapping shifts or employee unavailability. To identify these problems, I created a separate validation module.

The system detects the following conflicts:

- Zero Coverage
- Insufficient Staffing
- Shift Overlap
- Availability Violation
- Missing Roster
- Multiple Brand Impact
- Weekly Off Preference Changed
- Weekly Rest Violation

I divided these conflicts into two categories, Critical and Warning. Critical conflicts need to be resolved before approving the roster, while warnings need to be reviewed.

The Conflict Reports page shows the reason for the conflict, affected employee, brand, process and suggested action.

### 6. Which decisions are automated and which remain under human control?

According to me, automating everything is not a good idea in this type of application because there are some situations where a manager needs to make the decision.

For example, if an employee is unavailable and there is no backup employee, the system can identify the problem but the manager should decide how to handle it.

So in this project, I automated things like roster generation, weekly-off adjustments, coverage calculation and conflict detection.

Things like assigning employees to brands, setting staffing requirements and making manual changes are under the manager's control.

I also added an Impact Analysis feature where the manager can see what will happen if a particular change is made to the roster. It compares the conflicts before and after the change.

The reason behind adding this feature was to help the manager understand the impact before saving any changes.

### 7. How would the system scale if the number of employees and brands doubled?

If the number of employees and brands doubles, the system will have more data to process and more conflicts to check.

Since I divided the project into separate modules, adding more employees, brands and processes does not require changing the entire application.

However, I would need to improve some areas like database queries and the scheduling algorithm. I would also add database indexes to improve query performance.

Currently, I am using SQLite, but for a larger application with multiple users, I would prefer PostgreSQL. I would also explore constraint-based scheduling to handle more complex scheduling requirements.

### 8. What improvements would be implemented with one additional week?

If I had one more week to work on this project, the first thing I would improve is the scheduling algorithm because the current algorithm can generate a roster but cannot resolve all the conflicts.

I would also like to add a feature that suggests backup employees whenever there is a staffing shortage.

Some other improvements would be:

- Better distribution of weekly offs.
- User login and role-based access.
- Maintaining a history of roster changes.
- Permanent cloud database storage using PostgreSQL.
- Better employee rest and availability checks.
- Support for multiple users.
- More testing with different scheduling situations.

My main priority would be reducing conflicts and making the application more suitable for actual business use.

## Testing

I used Pytest to test the important functions of the application because a small error in scheduling can affect multiple employees and brands.

The automated tests cover:

- Monthly date generation and leap years.
- Brand operating rules.
- Minimum staffing requirements.
- Staffing shortages.
- Overlapping shifts.
- Weekly rest validation.
- Conflict comparison.

To run the tests:

    python -m pytest tests/ -v

Apart from automated testing, I also included manual testing scenarios like generating a roster, changing employee availability and checking the impact of those changes.

## Assumptions and Limitations

There are some assumptions I made while developing this project and some limitations in the current version.

- All employee and brand data is fictional.
- Shifts start and end on the same day.
- Weekly offs may be changed to reduce staffing shortages.
- The scheduling algorithm does not guarantee the best possible roster.
- Employees with overlapping assignments are excluded from confirmed coverage for the affected processes.
- Weekly rest validation only checks complete weeks within the selected month.
- Generating a roster again for the same month may replace manual changes.
- Some staffing calculations do not consider overlapping assignments.
- SQLite database changes may be lost after restarting or redeploying the application.
- User authentication and permanent roster change history are not included.

## Development Approach

I divided this project into different phases instead of developing everything at once.

First, I worked on the database and sample data. After that, I developed employee management, brand management and roster generation.

Once these things were working, I moved towards conflict detection, roster editing and impact analysis. In the final phases, I worked on testing, improving the user interface, uploading the project to GitHub and deploying it on Streamlit.

My main purpose was not only to generate a roster but also to identify the problems in it and help the manager understand those problems.

During the development of this project, I used AI assistance for guidance, understanding concepts, code generation and solving errors.

## Author

**Naveen Kumar Sharanappa Nayak**
