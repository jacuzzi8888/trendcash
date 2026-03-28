import csv
import sys
from datetime import datetime, timezone

from app.db import get_db, init_db, utc_now


REQUIRED_FIELDS = [
    "topic",
    "category",
    "source",
    "velocity_score",
    "advertiser_safety_score",
    "commercial_intent_score",
    "evergreen_score",
]


def parse_float(value, field):
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"{field} must be numeric: {value}")


def main(path):
    init_db()
    conn = get_db()
    inserted = 0
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for field in REQUIRED_FIELDS:
            if field not in reader.fieldnames:
                raise ValueError(f"Missing required column: {field}")

        for row in reader:
            created_at = row.get("created_at") or utc_now()
            try:
                datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except ValueError:
                created_at = utc_now()

            conn.execute(
                """
                INSERT INTO trend_candidates
                (topic, category, source, velocity_score, advertiser_safety_score,
                 commercial_intent_score, evergreen_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["topic"].strip(),
                    row["category"].strip(),
                    row["source"].strip(),
                    parse_float(row["velocity_score"], "velocity_score"),
                    parse_float(row["advertiser_safety_score"], "advertiser_safety_score"),
                    parse_float(row["commercial_intent_score"], "commercial_intent_score"),
                    parse_float(row["evergreen_score"], "evergreen_score"),
                    created_at,
                ),
            )
            inserted += 1

    conn.commit()
    conn.close()
    print(f"Imported {inserted} trend candidates.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/import_trends.py path/to/trends.csv")
        sys.exit(1)
    main(sys.argv[1])
