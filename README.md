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

The main problem in generating a roster is managing employee availability while also meeting the staffing requirements of different brands. Every employee has different weekly offs, leaves and work responsibilities.

To handle this, I used a rule-based scheduling approach. The scheduler first collects all the required data from the database and gives priority to approved leaves and mandatory holidays. After that, it assigns weekly offs based on employee preferences. If a weekly off causes a staffing shortage, the scheduler tries to move it to another day within the same week without creating another shortage.

Once the roster is generated, the validator checks for different scheduling conflicts. If the system cannot meet all the requirements, it reports those conflicts so the manager can review and resolve them.

## Assessment Questions

### 1. How are employees, brands, processes and pods related?

In this project, one employee can work for multiple brands, and one brand can have multiple processes. To manage these relationships, I used a relational SQLite database.

Every employee belongs to a pod, and every pod has a team leader. I created a `brand_processes` table to connect brands with their processes and store their operating rules and staffing requirements.

The `assignments` table connects employees with brand processes using a many-to-many relationship. This allows multiple employees to work on the same process and one employee to handle multiple processes. I also created separate tables for leaves, holidays, staffing requirements and roster records.

### 2. How does the roster generation logic work?

Before generating a roster, we need to know which employees are available and how many employees are required for each process.

The scheduler first collects this information from the database and generates all the dates for the selected month. It then assigns daily statuses to employees based on their leaves, holidays and weekly-off preferences.

If there is a staffing shortage, the scheduler tries to adjust the weekly offs using a greedy approach. While making these adjustments, it also checks whether moving a weekly off creates another staffing shortage.

After completing this process, the roster is saved in the database and checked by the validator. If there are still conflicts, the system reports them instead of ignoring them.

### 3. How does the system handle single-resource and multi-resource brands?

The main difference between single-resource and multi-resource brands is the number of employees assigned to them.

In a single-resource brand, there is only one dedicated employee, so if that employee is unavailable, it can directly affect the brand's operations.

In a multi-resource brand, there are multiple employees assigned to handle the work. If one employee is unavailable, the system checks whether the remaining employees can meet the minimum staffing requirement.

I implemented coverage checking at the brand-process level because different processes may have different staffing requirements. The system also checks for overlapping assignments and excludes those employees from confirmed coverage for the affected processes.

### 4. What happens when the only assigned employee becomes unavailable?

If a brand depends on only one employee and that employee becomes unavailable, there is a possibility that the brand's operations will be affected.

To handle this situation, the system first identifies the processes assigned to that employee. It then checks whether any other assigned employee is available to handle those processes.

If no employee is available, the system generates a Zero Coverage conflict and marks it as critical. The manager can review the conflict and decide whether to assign a backup employee or change the resource assignments.

The system does not automatically cancel approved leaves or override mandatory availability restrictions to solve the problem.

### 5. How are scheduling conflicts and insufficient staffing handled?

Generating a roster does not always mean that all staffing requirements have been fulfilled. There can still be situations where employees are unavailable, shifts overlap or a process does not have enough employees.

To identify these problems, I created a separate validation module.

The system detects the following conflicts:

- Zero Coverage
- Insufficient Staffing
- Shift Overlap
- Availability Violation
- Missing Roster
- Multiple Brand Impact
- Weekly Off Preference Changed
- Weekly Rest Violation

I divided these conflicts into two categories: Critical and Warning. Critical conflicts require attention before approving the roster, while warnings indicate situations that need review.

The Conflict Reports page displays the affected employee, date, brand, process and reason for the conflict. It also provides a suggested action to help the manager resolve the problem.

### 6. Which decisions are automated and which remain under human control?

I believe that automating every decision in workforce management is not always a good approach because some decisions require human judgment.

In this project, I automated tasks such as roster generation, weekly-off adjustments, coverage calculation and conflict detection. These are repetitive tasks that can be handled using predefined rules.

However, decisions such as assigning employees to brands, setting staffing requirements and making manual roster changes remain under the manager's control.

I also added an Impact Analysis feature to help managers understand the effect of a change before saving it. For example, if a manager makes an employee unavailable, the system compares the conflicts before and after that change.

This helps reduce manual work while still allowing the manager to make the final decision.

### 7. How would the system scale if the number of employees and brands doubled?

If the number of employees and brands increases, the system will have to process more records and perform more coverage and conflict calculations.

Since I divided the application into separate modules, new employees, brands, processes and pods can be added without changing the main application logic.

However, for a larger system, I would reduce repeated database queries, add database indexes and improve the scheduling algorithm.

Currently, I am using SQLite, which is suitable for this project. For a larger application with multiple users, I would consider PostgreSQL because it provides better support for concurrent database operations and permanent cloud storage.

I would also explore constraint-based scheduling to handle more complex staffing requirements.

### 8. What improvements would be implemented with one additional week?

The current application can generate rosters, detect conflicts and show the impact of manual changes. However, there are still some areas where the application can be improved.

If I had one more week, my first priority would be improving the scheduling algorithm to reduce the number of conflicts. I would also add a feature that recommends suitable backup employees when a staffing shortage occurs.

Apart from this, I would work on the following improvements:

- Fairer distribution of weekly offs.
- Better employee rest and availability checks.
- User login and role-based access.
- Maintaining a history of roster changes.
- Permanent database storage using PostgreSQL.
- Better support for multiple users.
- Additional testing for different scheduling situations.

These improvements would make the application more useful for real-world workforce management.

## Testing

Testing is important in this project because even a small error in the scheduling logic can affect multiple employees, brands and processes.

I used Pytest to test the important functions of the application.

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

Apart from automated testing, I also included manual testing scenarios such as generating a monthly roster, making an employee unavailable and checking the impact of manual changes.

The purpose of these tests is to check whether the application behaves as expected in different scheduling situations.

## Assumptions and Limitations

While developing this project, I made some assumptions to keep the scheduling logic manageable. There are also some limitations in the current version that can be improved in the future.

- All employee and brand data used in this project is fictional.
- Shift timings are assumed to start and end on the same day.
- Employee weekly offs may be adjusted to improve staffing coverage.
- The scheduling algorithm tries to reduce conflicts but does not guarantee the best possible roster.
- Employees with overlapping assignments are excluded from confirmed coverage for the affected processes.
- Weekly rest validation checks complete weeks within the selected month.
- Regenerating a roster for the same month may replace previous manual changes.
- Some conflict calculations use scheduled employee counts without considering overlapping assignments.
- SQLite database changes may be lost after the deployed application restarts or is redeployed.
- User authentication and permanent roster change history are not included in the current version.

## Development Approach

Instead of developing the entire application at once, I divided the project into smaller phases.

I first worked on the database structure and sample data because they are the foundation of the application. After that, I developed the employee management, brand management and roster generation features.

Once the roster generation was working, I focused on conflict detection, manual roster editing and impact analysis. In the final phases, I worked on the user interface, testing, GitHub and Streamlit deployment.

My main goal was not just to generate a roster but also to identify the problems within it and help managers make better scheduling decisions.

During the development process, I used AI assistance for guidance, code generation, understanding concepts and debugging errors.

## Author

**Naveen Kumar Sharanappa Nayak**
