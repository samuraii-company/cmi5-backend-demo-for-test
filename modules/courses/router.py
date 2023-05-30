from uuid import UUID

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile

from modules.courses.schema import (
    CMICourseRead,
    CMICoursesBase,
    CMIEnrollementCreate,
    CMIEnrollementRead,
)
from modules.courses.service import CMICourseService, CourseDTO
from modules.users.services import UserService
import logging
from storage.storage import IStorage, LocalStorage


logger = logging.getLogger(__name__)

courses_router = APIRouter(tags=["courses"], prefix="/api/courses")


@courses_router.post(
    "",
    response_model=CMICourseRead,
)
async def create_cmi5_course(
    title: str = Body(..., description="Course Title"),
    description: str = Body(..., description="Course Description"),
    file: UploadFile = File(...),
    cmi_course_service: CMICourseService = Depends(CMICourseService),
    storage: IStorage = Depends(LocalStorage),
):
    """Create CMI5 Course"""

    if file.content_type not in ("application/zip", "application/octet-stream"):
        raise HTTPException(detail="upload zip archive", status_code=400)

    file_path = storage.save_course_file(file)

    data = CourseDTO(title=title, description=description, file_path=file_path)

    course = await cmi_course_service.create(data)

    return course


@courses_router.get("/all", response_model=list[CMICoursesBase])
async def get_cmi5_all_courses(
    cmi_course_service: CMICourseService = Depends(CMICourseService),
):
    """Get all courses"""

    courses = await cmi_course_service.get_all()

    return courses


@courses_router.get(
    "/{course_id}",
    response_model=CMICourseRead,
)
async def get_cmi5_course(
    course_id: UUID,
    cmi_course_service: CMICourseService = Depends(CMICourseService),
):
    """Get course detail with users"""

    course = await cmi_course_service.get_by_id(course_id)

    if not course:
        raise HTTPException(detail="Курс не найден", status_code=404)

    course = CMICourseRead.from_orm(course)
    course.users = await cmi_course_service.get_users(course)

    return course


@courses_router.post(
    "/enrollment",
    name="cmi5:set_enrollment",
    response_model=CMIEnrollementRead,
)
async def set_enrollment(
    data: CMIEnrollementCreate,
    user_service: UserService = Depends(UserService),
    cmi_course_service: CMICourseService = Depends(CMICourseService),
):
    """Set Course on user"""

    course = await cmi_course_service.get_by_id(data.course_id)

    if not course:
        raise HTTPException(detail="Курс не найден", status_code=404)

    user = await user_service.get_by_id(data.user_id)

    if not user:
        raise HTTPException(detail="Пользователь не найден", status_code=404)

    enrollment = await cmi_course_service.get_enrollment(course.id, user.id)

    if enrollment:
        raise HTTPException(
            detail="Курс уже назначен на пользователя",
            status_code=400,
        )

    enrollment = await cmi_course_service.set_enrollment(course, user)
    return enrollment
