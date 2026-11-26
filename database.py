import sqlite3 
from pathlib import Path

DB_NAME= Path(__file__).resolve().parent / "roster.db"

def get_connection():
    conn=sqlite3.connect(DB_NAME)
    conn.execute("Pragma foreign_keys = ON")
    return conn

def create_tables():
    conn=get_connection()
    cursor=conn.cursor()

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS pods(
    pod_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pod_name TEXT NOT NULL UNIQUE,
    pod_lead TEXT NOT NULL);

    CREATE TABLE IF NOT EXISTS employees(
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    pod_id INTEGER NOT NULL,
    weekly_off TEXT NOT NULL,
    holiday_off INTEGER DEFAULT 1,
    FOREIGN KEY (pod_id) REFERENCES pods(pod_id)
    );

    CREATE TABLE IF NOT EXISTS processes (
        process_id INTEGER PRIMARY KEY AUTOINCREMENT,
        process_name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS brands (
    brand_id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS brand_processes (
        brand_process_id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_id INTEGER NOT NULL,
        process_id INTEGER NOT NULL,
        working_rule TEXT NOT NULL,
        min_staff INTEGER NOT NULL DEFAULT 1
            CHECK (min_staff >= 1),
        sunday_min_staff INTEGER
            CHECK (sunday_min_staff >= 1),
        UNIQUE (brand_id, process_id),
        FOREIGN KEY (brand_id) REFERENCES brands(brand_id),
        FOREIGN KEY (process_id) REFERENCES processes(process_id)
    );

    CREATE TABLE IF NOT EXISTS staffing_rules (

    rule_id INTEGER PRIMARY KEY AUTOINCREMENT,

    brand_process_id INTEGER NOT NULL,

    weekday INTEGER NOT NULL
        CHECK(weekday BETWEEN 0 AND 6),

    min_staff INTEGER NOT NULL
        CHECK(min_staff >= 1),

    UNIQUE(brand_process_id, weekday),

    FOREIGN KEY (brand_process_id)
        REFERENCES brand_processes(brand_process_id)
        ON DELETE CASCADE

);

    CREATE TABLE IF NOT EXISTS assignments (
        assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        brand_process_id INTEGER NOT NULL,
        start_time TEXT NOT NULL DEFAULT '09:00',
        end_time TEXT NOT NULL DEFAULT '18:00',
        UNIQUE (employee_id, brand_process_id),
        FOREIGN KEY (employee_id)
            REFERENCES employees(employee_id),
        FOREIGN KEY (brand_process_id)
            REFERENCES brand_processes(brand_process_id)
    );

    CREATE TABLE IF NOT EXISTS leaves (
        leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        leave_date TEXT NOT NULL,
        leave_type TEXT NOT NULL,
        reason TEXT,
        UNIQUE (employee_id, leave_date),
        FOREIGN KEY (employee_id)
            REFERENCES employees(employee_id)
    );

    CREATE TABLE IF NOT EXISTS holidays (
        holiday_id INTEGER PRIMARY KEY AUTOINCREMENT,
        holiday_date TEXT NOT NULL UNIQUE,
        holiday_name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS roster (
        roster_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        work_date TEXT NOT NULL,
        status TEXT NOT NULL,
        UNIQUE (employee_id, work_date),
        FOREIGN KEY (employee_id)
            REFERENCES employees(employee_id)
    );

    ''')

    conn.commit()
    conn.close()

    print("All database tables created successfully!")


if __name__ == "__main__":
    create_tables()

      