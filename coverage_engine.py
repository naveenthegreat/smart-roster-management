from itertools import combinations

from scheduler import is_process_open


def get_overlapping_assignments(
    dates,
    processes,
    assignments,
    roster_lookup,
    holiday_dates
):

    blocked = set()

    process_map = {
        row["brand_process_id"]: row
        for _, row in processes.iterrows()
    }

    for emp_id, group in assignments.groupby("employee_id"):

        records = group.to_dict("records")

        for current_date in dates:

            date_string = current_date.isoformat()

            if roster_lookup.get(
                (emp_id, date_string)
            ) != "W":
                continue

            active = [
                assignment
                for assignment in records
                if is_process_open(
                    process_map[assignment["brand_process_id"]],
                    current_date,
                    holiday_dates
                )
            ]

            for first, second in combinations(active, 2):

                if (
                    first["start_time"] < second["end_time"]
                    and
                    second["start_time"] < first["end_time"]
                ):

                    for assignment in [first, second]:

                        blocked.add((
                            emp_id,
                            assignment["brand_process_id"],
                            date_string
                        ))

    return blocked