
from database import get_connection
import pandas as pd

conn = get_connection()

query = """
SELECT
    b.brand_name,
    COUNT(DISTINCT a.employee_id) AS employee_count

FROM brands b

LEFT JOIN brand_processes bp
    ON b.brand_id = bp.brand_id

LEFT JOIN assignments a
    ON bp.brand_process_id = a.brand_process_id

GROUP BY b.brand_id, b.brand_name

ORDER BY b.brand_id
"""

df = pd.read_sql_query(query, conn)

print(df.to_string(index=False))

single = (df["employee_count"] == 1).sum()
multiple = (df["employee_count"] > 1).sum()

print("\nSingle-resource brands:", single)
print("Multi-resource brands:", multiple)

print("Single-resource percentage:",
      single / len(df) * 100)

conn.close()
