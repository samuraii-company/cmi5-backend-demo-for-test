from uuid import UUID

from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from modules.courses.schema import (
    CMICourseRead,
    CMICoursesBase,
    CMIEnrollementCreate,
    CMIEnrollementRead,
)
from modules.courses.service import CMICourseService, CourseDTO
from modules.users.services import UserService
import logging
from shared.utils import extract_zip
from storage.storage import IStorage, LocalStorage
from shutil import rmtree
import os.path

logger = logging.getLogger(__name__)

courses_router = APIRouter(tags=["courses"], prefix="/api/courses")


@courses_router.post(
    "", response_model=CMICourseRead, name="courses:create_cmi5_course"
)
async def create_cmi5_course(
    title: str = Body(..., description="Course Title"),
    description: str = Body(..., description="Course Description"),
    file: UploadFile = File(...),
    cmi_course_service: CMICourseService = Depends(CMICourseService),
    storage: IStorage = Depends(LocalStorage),
):
    """Create CMI5 Course"""

    content_type = ""

    if file.content_type in (
        "application/zip",
        "application/octet-stream",
        "application/x-zip-compressed",
    ):
        content_type = "zip"
    else:
        raise HTTPException(
            detail="Uploading Failed: Bad archive or file",
            status_code=400,
        )

    folder_path = extract_zip(file)

    if content_type == "zip" and not os.path.exists(f"{folder_path}/cmi5.xml"):
        rmtree(folder_path)
        raise HTTPException(
            detail="Failed to retrieve course structure data from zip: not found cmi5.xml file",
            status_code=400,
        )

    file_path = storage.save_course_folder(folder_path)

    data = CourseDTO(
        title=title,
        description=description,
        file_path=os.path.join(file_path, "res/index.html"),
    )

    course = await cmi_course_service.create(data)
    # delete local folder after uploading scorm course on s3 bucket
    rmtree(folder_path)
    return course


@courses_router.get(
    "/all", response_model=list[CMICoursesBase], name="courses:get_cmi5_all_courses"
)
async def get_cmi5_all_courses(
    cmi_course_service: CMICourseService = Depends(CMICourseService),
):
    """Get all courses"""

    courses = await cmi_course_service.get_all()

    return courses


@courses_router.get(
    "/{course_id}", response_model=CMICourseRead, name="courses:get_cmi5_course"
)
async def get_cmi5_course(
    course_id: UUID,
    cmi_course_service: CMICourseService = Depends(CMICourseService),
):
    """Get course with users by this course"""

    course = await cmi_course_service.get_by_id(course_id)

    if not course:
        raise HTTPException(detail="Курс не найден", status_code=404)

    course = CMICourseRead.from_orm(course)
    course.users = await cmi_course_service.get_users(course)

    return course


@courses_router.post(
    "/enrollment",
    name="courses:set_enrollment",
    response_model=CMIEnrollementRead,
)
async def set_enrollment(
    data: CMIEnrollementCreate,
    user_service: UserService = Depends(UserService),
    cmi_course_service: CMICourseService = Depends(CMICourseService),
):
    """Assign course on user"""
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
