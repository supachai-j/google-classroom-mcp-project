import csv
from pathlib import Path
from typing import Any

from . import classroom


def compute_final_grades(course_id: str, weights: dict[str, float]) -> list[dict[str, Any]]:
    """Compute weighted final grades.

    weights: { coursework_id: weight } — weights should sum to 1.0.
    Returns one row per student with per-coursework normalized contribution and total (0-100).
    """
    weight_sum = sum(weights.values())
    if abs(weight_sum - 1.0) > 1e-3:
        raise ValueError(f"weights must sum to 1.0, got {weight_sum:.4f}")

    students = {s["userId"]: s for s in classroom.list_students(course_id)}
    coursework_meta: dict[str, dict[str, Any]] = {}
    grades_by_student: dict[str, dict[str, float | None]] = {uid: {} for uid in students}

    for cw_id in weights:
        cw = classroom.get_coursework(course_id, cw_id)
        coursework_meta[cw_id] = {
            "title": cw.get("title"),
            "maxPoints": cw.get("maxPoints", 100),
        }
        for sub in classroom.list_submissions(course_id, cw_id):
            uid = sub.get("userId")
            if uid in grades_by_student:
                grades_by_student[uid][cw_id] = sub.get("assignedGrade")

    results: list[dict[str, Any]] = []
    for uid, scores in grades_by_student.items():
        profile = students[uid].get("profile", {})
        total = 0.0
        missing: list[str] = []
        for cw_id, weight in weights.items():
            g = scores.get(cw_id)
            if g is None:
                missing.append(coursework_meta[cw_id]["title"] or cw_id)
                continue
            max_pts = coursework_meta[cw_id]["maxPoints"] or 100
            total += (g / max_pts) * weight * 100

        results.append(
            {
                "userId": uid,
                "name": profile.get("name", {}).get("fullName"),
                "email": profile.get("emailAddress"),
                "scores": {coursework_meta[cw]["title"] or cw: scores.get(cw) for cw in weights},
                "total": round(total, 2),
                "missing": missing,
            }
        )
    return results


def export_grades_csv(course_id: str, weights: dict[str, float], output_path: str) -> str:
    results = compute_final_grades(course_id, weights)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    cw_titles = list(next(iter(results), {"scores": {}})["scores"].keys()) if results else []
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["userId", "name", "email", *cw_titles, "total", "missing"])
        for r in results:
            writer.writerow(
                [
                    r["userId"],
                    r["name"],
                    r["email"],
                    *[r["scores"].get(t, "") for t in cw_titles],
                    r["total"],
                    " | ".join(r["missing"]),
                ]
            )
    return str(out)
