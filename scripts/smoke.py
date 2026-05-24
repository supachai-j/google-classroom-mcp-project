"""End-to-end smoke test — verifies OAuth + a real Classroom read.

Run after dropping secrets/credentials.json into place:
    uv run python scripts/smoke.py

First run opens a browser for OAuth consent and writes secrets/token.json.
Subsequent runs are silent (refresh token).
"""

from google_classroom_mcp import classroom


def main() -> None:
    print("1/3 listing courses...")
    courses = classroom.list_courses(active_only=True)
    print(f"    found {len(courses)} active course(s)")
    for c in courses:
        print(f"      [{c['id']}] {c['name']} (section: {c.get('section') or '-'})")

    if not courses:
        print("\nno active courses — smoke test stops here. auth + connectivity verified.")
        return

    first = courses[0]
    course_id = first["id"]
    print(f"\n2/3 listing students of course '{first['name']}'...")
    students = classroom.list_students(course_id)
    print(f"    found {len(students)} student(s)")
    for s in students[:5]:
        profile = s.get("profile", {})
        name = profile.get("name", {}).get("fullName", "?")
        email = profile.get("emailAddress", "?")
        print(f"      - {name} <{email}>")
    if len(students) > 5:
        print(f"      ... and {len(students) - 5} more")

    print(f"\n3/3 listing coursework of course '{first['name']}'...")
    coursework = classroom.list_coursework(course_id)
    print(f"    found {len(coursework)} coursework item(s)")
    for cw in coursework[:5]:
        max_pts = cw.get("maxPoints", "-")
        print(f"      [{cw['id']}] {cw.get('title', '?')} (max {max_pts}, state: {cw.get('state')})")
    if len(coursework) > 5:
        print(f"      ... and {len(coursework) - 5} more")

    print("\nsmoke test passed.")


if __name__ == "__main__":
    main()
