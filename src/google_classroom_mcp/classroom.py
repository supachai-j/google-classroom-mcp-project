from functools import lru_cache
from typing import Any

from googleapiclient.discovery import build

from .auth import get_credentials


@lru_cache(maxsize=1)
def _service():
    return build("classroom", "v1", credentials=get_credentials(), cache_discovery=False)


def _paginate(request_fn, response_key: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    page_token: str | None = None
    while True:
        resp = request_fn(pageToken=page_token).execute()
        items.extend(resp.get(response_key, []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            return items


def list_courses(active_only: bool = True) -> list[dict[str, Any]]:
    svc = _service()
    kwargs: dict[str, Any] = {"teacherId": "me"}
    if active_only:
        kwargs["courseStates"] = ["ACTIVE"]
    return _paginate(lambda pageToken: svc.courses().list(pageToken=pageToken, **kwargs), "courses")


def list_students(course_id: str) -> list[dict[str, Any]]:
    svc = _service()
    return _paginate(
        lambda pageToken: svc.courses().students().list(courseId=course_id, pageToken=pageToken),
        "students",
    )


def list_coursework(course_id: str) -> list[dict[str, Any]]:
    svc = _service()
    return _paginate(
        lambda pageToken: svc.courses().courseWork().list(courseId=course_id, pageToken=pageToken),
        "courseWork",
    )


def get_coursework(course_id: str, coursework_id: str) -> dict[str, Any]:
    svc = _service()
    return svc.courses().courseWork().get(courseId=course_id, id=coursework_id).execute()


def list_submissions(course_id: str, coursework_id: str) -> list[dict[str, Any]]:
    svc = _service()
    return _paginate(
        lambda pageToken: svc.courses()
        .courseWork()
        .studentSubmissions()
        .list(courseId=course_id, courseWorkId=coursework_id, pageToken=pageToken),
        "studentSubmissions",
    )


def grade_submission(
    course_id: str,
    coursework_id: str,
    submission_id: str,
    grade: float,
    draft: bool = False,
) -> dict[str, Any]:
    svc = _service()
    body: dict[str, Any] = {"draftGrade": grade}
    update_mask = "draftGrade"
    if not draft:
        body["assignedGrade"] = grade
        update_mask = "assignedGrade,draftGrade"
    return (
        svc.courses()
        .courseWork()
        .studentSubmissions()
        .patch(
            courseId=course_id,
            courseWorkId=coursework_id,
            id=submission_id,
            updateMask=update_mask,
            body=body,
        )
        .execute()
    )


def return_submission(course_id: str, coursework_id: str, submission_id: str) -> dict[str, Any]:
    svc = _service()
    return (
        svc.courses()
        .courseWork()
        .studentSubmissions()
        .return_(
            courseId=course_id,
            courseWorkId=coursework_id,
            id=submission_id,
            body={},
        )
        .execute()
    )
