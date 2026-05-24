"""Example cohort config for `build_final_grading.py`.

Copy this file to `data/<your_cohort>.py` (which is gitignored) and edit with
real student data. The grading script reads this module via CLI arg:

    python scripts/build_final_grading.py data/your_cohort.py

Required module-level names: COHORT_NAME, COHORT_TITLE, OUTPUT, STUDENTS,
QUALITY_ADJUST, REVIEW_POINTS.

This example uses placeholder values that match the script's expected types.
"""

COHORT_NAME = "EXAMPLE_2026_01"
COHORT_TITLE = "Example Course (Cohort 1) — Final Grading"
OUTPUT = "example_grading.xlsx"

# Each student dict:
#   id, first, last, nick, classroom, email — identification
#   note — free-form note in the Summary section
#   labs — list of 17 status strings, one per LAB0..LAB16:
#          "ok"   = turned in on time
#          "late" = turned in after deadline
#          "no"   = not submitted
STUDENTS = [
    {
        "id": "0000000001",
        "first": "Firstname",
        "last": "Lastname",
        "nick": "Nick",
        "classroom": "Classroom Display Name",
        "email": "student@example.com",
        "note": "",
        "labs": ["ok"] * 17,
    },
    {
        "id": "0000000002",
        "first": "Another",
        "last": "Student",
        "nick": "",
        "classroom": "Another Student",
        "email": "another@example.com",
        "note": "missed some labs",
        "labs": ["ok"] * 7 + ["late"] * 4 + ["no"] * 6,
    },
]

# Per-student per-lab quality adjustment:
#   { student_id: { lab_idx: {"mult": 0.0..1.0, "note": "..."} } }
# - mult 0.0  → 0 credit (empty file, submitted template, wrong-file)
# - mult 0.5  → half credit (partial answer, missing key commands)
# - mult 0.75 → 75% credit (minor gap)
# - mult 1.0  → full credit; "note" appears as informational flag for the grader
QUALITY_ADJUST: dict[str, dict[int, dict]] = {
    # "0000000001": {
    #     7: {"mult": 0.0, "note": "Submitted template, no actual answer"},
    #     11: {"mult": 0.75, "note": "OSPF on only 3 of 4 routers"},
    # },
}

# Free-form bullet points that appear under "สรุปจุดสำคัญที่อาจารย์ต้องดูเพิ่ม"
# at the bottom of the workbook. Use to call out cross-student patterns or
# items that need manual instructor review.
REVIEW_POINTS = [
    # "1. Multiple students submitted empty LAB5 — check Classroom assignment for issues",
]
