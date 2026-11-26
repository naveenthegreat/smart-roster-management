
from database import get_connection

conn = get_connection()
cursor = conn.cursor()

tables = [
    "pods",
    "employees",
    "brands",
    "processes",
    "brand_processes",
    "assignments",
    "leaves",
    "holidays",
    "roster"
]

print("DATABASE SUMMARY")
print("-" * 30)

for table in tables:

    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]

    print(f"{table}: {count}")

conn.close()
