from typing import Any

from fastmcp import FastMCP

from . import classroom, drive, grades

mcp = FastMCP("google-classroom")


@mcp.tool
def list_courses(active_only: bool = True) -> list[dict[str, Any]]:
    """List Google Classroom courses the authenticated user teaches."""
    return [
        {
            "id": c["id"],
            "name": c["name"],
            "section": c.get("section"),
            "room": c.get("room"),
            "state": c.get("courseState"),
            "enrollmentCode": c.get("enrollmentCode"),
        }
        for c in classroom.list_courses(active_only=active_only)
    ]


@mcp.tool
def list_students(course_id: str) -> list[dict[str, Any]]:
    """List students enrolled in a course."""
    return [
        {
            "userId": s["userId"],
            "name": s.get("profile", {}).get("name", {}).get("fullName"),
            "email": s.get("profile", {}).get("emailAddress"),
        }
        for s in classroom.list_students(course_id)
    ]


@mcp.tool
def list_coursework(course_id: str) -> list[dict[str, Any]]:
    """List assignments / coursework items in a course."""
    return [
        {
            "id": cw["id"],
            "title": cw.get("title"),
            "workType": cw.get("workType"),
            "maxPoints": cw.get("maxPoints"),
            "dueDate": cw.get("dueDate"),
            "state": cw.get("state"),
        }
        for cw in classroom.list_coursework(course_id)
    ]


@mcp.tool
def list_submissions(course_id: str, coursework_id: str) -> list[dict[str, Any]]:
    """List student submissions for a coursework item."""
    return [
        {
            "submissionId": s["id"],
            "userId": s.get("userId"),
            "state": s.get("state"),
            "late": s.get("late", False),
            "assignedGrade": s.get("assignedGrade"),
            "draftGrade": s.get("draftGrade"),
            "attachments": [
                {
                    "driveFileId": a.get("driveFile", {}).get("id"),
                    "title": a.get("driveFile", {}).get("title"),
                    "alternateLink": a.get("driveFile", {}).get("alternateLink"),
                }
                for a in s.get("assignmentSubmission", {}).get("attachments", [])
                if "driveFile" in a
            ],
        }
        for s in classroom.list_submissions(course_id, coursework_id)
    ]


@mcp.tool
def read_drive_file(file_id: str, max_bytes: int = 200_000) -> dict[str, Any]:
    """Read the text content of a Drive file (or attachment). Google Docs/Sheets/Slides are exported automatically."""
    return drive.fetch_file_text(file_id, max_bytes=max_bytes)


@mcp.tool
def grade_submission(
    course_id: str,
    coursework_id: str,
    submission_id: str,
    grade: float,
    draft: bool = False,
) -> dict[str, Any]:
    """Set a grade on a submission. Set draft=True to save as draft only (not visible to student)."""
    return classroom.grade_submission(course_id, coursework_id, submission_id, grade, draft=draft)


@mcp.tool
def return_submission(course_id: str, coursework_id: str, submission_id: str) -> dict[str, Any]:
    """Return a graded submission to the student (releases the assigned grade)."""
    return classroom.return_submission(course_id, coursework_id, submission_id)


@mcp.tool
def compute_final_grades(course_id: str, weights: dict[str, float]) -> list[dict[str, Any]]:
    """Compute weighted final grades. weights = { coursework_id: weight }, summing to 1.0."""
    return grades.compute_final_grades(course_id, weights)


@mcp.tool
def export_grades_csv(course_id: str, weights: dict[str, float], output_path: str) -> str:
    """Compute final grades and write to a CSV file. Returns the written path."""
    return grades.export_grades_csv(course_id, weights, output_path)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
