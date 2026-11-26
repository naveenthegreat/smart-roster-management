from database import get_connection, create_tables
from datetime import date

def seed_pods(cursor):
    pods=[
        ("Alpha", "Rahul Sharma"),
        ("Beta", "Priya Patel"),
        ("Gamma", "Amit Verma"),
        ("Delta", "Sneha Joshi"),
        ("Omega","Karan Singh"),
    ]

    cursor.executemany("""
        INSERT INTO pods (pod_name, pod_lead)
        VALUES (?, ?)
    """, pods)

def seed_employees(cursor):
    names = [
        "Rahul Sharma", "Ananya Rao", "Rohit Kumar",
        "Meera Shah", "Arjun Nair", "Pooja Gupta",

        "Priya Patel", "Vikram Das", "Neha Jain",
        "Aditya Singh", "Riya Kapoor", "Manish Yadav",

        "Amit Verma", "Kavya Reddy", "Sahil Khan",
        "Divya Menon", "Akash Roy", "Nisha Sinha",

        "Sneha Joshi", "Varun Mehta", "Isha Kulkarni",
        "Deepak Mishra", "Tanvi Desai", "Harsh Shah",

        "Karan Singh", "Simran Kaur", "Rohan Patil",
        "Aditi Sharma", "Yash Jain", "Anjali Rao"
    ]

    days=[
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    employees=[]

    for i, name in enumerate(names):
        pod_id = (i//6) + 1
        weekly_off = days[i%7]
        holiday_off = 0 if i % 3 == 0 else 1

        employees.append(
            (name,pod_id,weekly_off,holiday_off)
        )

    cursor.executemany("""
        INSERT INTO employees
        (name, pod_id, weekly_off, holiday_off)
        VALUES (?, ?, ?, ?)
    """, employees)

def seed_brands(cursor):
    brands=[
        "UrbanStyle", "GlowCare", "FreshBasket",
        "TechNova", "PureSkin", "FitFuel",
        "HomeNest", "EcoWear", "QuickCart",
        "BeautyBloom", "NutriLife", "StyleHub",
        "GreenLeaf", "SmartGadgets", "PetPal",
        "DailyNeeds", "ComfortZone", "BookNest",
        "HappyFeet", "OrganicRoots", "Trendify",
        "HealthPlus", "ShopSphere", "EliteWear",
        "NovaLiving"
    ]

    cursor.executemany("""
        INSERT INTO brands (brand_name)
        VALUES (?)
    """, [(name,) for name in brands])    

def seed_processes(cursor):
    processes=[
        ("Customer Support",),
        ("Abandoned Cart Conversion",),
        ("Non-Delivery Report",),
        ("Retention",)
    ]

    cursor.executemany("""
        INSERT INTO processes (process_name)
        VALUES (?)
    """, processes)

def seed_brand_processes(cursor):
    rules= [ 
        "ALL_DAYS",
        "NO_HOLIDAYS",
        "NO_SUNDAY_HOLIDAYS"
    ]

    for brand_id in range(1,26):
        process_count = 2 if brand_id <= 20 else 3

        for process_id in range(1, process_count + 1):

            working_rule = rules[
                (brand_id + process_id) % 3
            ]

            min_staff = 1
            sunday_min_staff = None

            if brand_id in [21,23,25] and process_id ==1:
                min_staff =2

                if working_rule != "NO_SUNDAY_HOLIDAYS":
                    sunday_min_staff = 1

            cursor.execute("""
                INSERT INTO brand_processes
                (
                    brand_id,
                    process_id,
                    working_rule,
                    min_staff,
                    sunday_min_staff
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                brand_id,
                process_id,
                working_rule,
                min_staff,
                sunday_min_staff
            ))

    for brand_id in [5,10,15,20,25]:
        cursor.execute("""
            INSERT INTO brand_processes
            (brand_id, process_id, working_rule, min_staff)
            VALUES (?, 4, 'NO_SUNDAY_HOLIDAYS',1)
        """, (brand_id,))


def seed_assignments(cursor):

    cursor.execute("""
        SELECT brand_process_id, brand_id, process_id
        FROM brand_processes
    """)

    brand_processes = cursor.fetchall()

    for bp_id, brand_id, process_id in brand_processes:

        if brand_id <= 20:

            employee_ids = [brand_id]

        else:

            first = 21 + (brand_id - 21) * 2
            second = first + 1

            if process_id == 1:
                employee_ids = [first, second]

            elif process_id == 2:
                employee_ids = [first]

            else:
                employee_ids = [second]

        for employee_id in employee_ids:

            slots = {
                1: ("09:00", "12:00"),
                2: ("12:00", "14:00"),
                3: ("14:00", "16:00"),
                4: ("16:00", "18:00")
            }

            start_time, end_time = slots[process_id]

            cursor.execute("""
                INSERT INTO assignments
                (
                    employee_id,
                    brand_process_id,
                    start_time,
                    end_time
                )
                VALUES (?, ?, ?, ?)
            """, (
                employee_id,
                bp_id,
                start_time,
                end_time
            ))

    cursor.execute("""
        SELECT brand_process_id
        FROM brand_processes
        WHERE brand_id = 22 AND process_id = 2
    """)

    bp_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO assignments
        (
            employee_id,
            brand_process_id,
            start_time,
            end_time
        )
        VALUES (?, ?, ?, ?)
    """, (21, bp_id, "12:00", "14:00"))


def seed_leaves(cursor):

    year = date.today().year

    leaves = [
        (1, f"{year}-12-04", "L", "Personal leave"),
        (3, f"{year}-12-08", "C", "Compensatory off"),
        (7, f"{year}-12-10", "L", "Family function"),
        (12, f"{year}-12-15", "U", "Unavailable"),
        (21, f"{year}-12-18", "L", "Planned leave"),
        (25, f"{year}-12-22", "C", "Compensatory off")
    ]

    cursor.executemany("""
        INSERT INTO leaves
        (employee_id, leave_date, leave_type, reason)
        VALUES (?, ?, ?, ?)
    """, leaves)


def seed_holidays(cursor):

    year = date.today().year

    holidays = [
        (f"{year}-01-26", "Republic Day"),
        (f"{year}-08-15", "Independence Day"),
        (f"{year}-10-02", "Gandhi Jayanti"),
        (f"{year}-12-25", "Christmas")
    ]

    cursor.executemany("""
        INSERT INTO holidays
        (holiday_date, holiday_name)
        VALUES (?, ?)
    """, holidays)


def seed_database():

    create_tables()

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("SELECT COUNT(*) FROM employees")

        if cursor.fetchone()[0] > 0:
            print("Sample data already exists.")
            return

        seed_pods(cursor)
        seed_employees(cursor)
        seed_brands(cursor)
        seed_processes(cursor)
        seed_brand_processes(cursor)
        seed_assignments(cursor)
        seed_leaves(cursor)
        seed_holidays(cursor)

        conn.commit()

        print("Sample data inserted successfully!")

    except Exception as error:

        conn.rollback()
        print("Error:", error)

    finally:

        conn.close()


if __name__ == "__main__":
    seed_database()
