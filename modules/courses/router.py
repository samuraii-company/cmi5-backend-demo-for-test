from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from modules.courses.schema import (
    CMICourseCreate,
    CMICourseRead,
    CMICoursesBase,
    CMIEnrollementCreate,
    CMIEnrollementRead,
)
from modules.courses.service import CMICourseService
from modules.users.services import UserService

courses_router = APIRouter(tags=["courses"], prefix="/api/courses")


@courses_router.post(
    "",
    response_model=CMICourseRead,
)
async def create_cmi5_course(
    data: CMICourseCreate,
    cmi_course_service: CMICourseService = Depends(CMICourseService),
):
    """Create CMI5 Course"""

    data = dict(
        title=data.title,
        description=data.description,
    )

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
        raise HTTPException("Курс не найден", status_code=404)

    user = await user_service.get_by_id(data.user_id)

    if not user:
        raise HTTPException("Пользователь не найден", status_code=404)

    enrollment = await cmi_course_service.get_enrollment(course.id, user.id)

    if enrollment:
        raise HTTPException(
            detail="Курс уже назначен на пользователя",
            status_code=400,
        )

    enrollment = await cmi_course_service.set_enrollment(course, user)

    return enrollment
