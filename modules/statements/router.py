from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from modules.courses.schema import CMICoursesBase

from modules.courses.service import CMICourseService
from modules.statements.schema import (
    CMIStatementBase,
    CMIStatementRead,
    CMIStatementsCreate,
)
from modules.statements.service import CMIStatementService

from modules.users.schema import UserRead

statement_router = APIRouter(tags=["statement"], prefix="/api/statement")


@statement_router.post(
    "", response_model=CMIStatementRead, name="statements:create_statement"
)
async def create_statement(
    data: CMIStatementsCreate,
    cmi_statement_service: CMIStatementService = Depends(CMIStatementService),
    cmi_course_service: CMICourseService = Depends(CMICourseService),
):
    """Create Statement"""

    enrollment = await cmi_course_service.get_enrollment(
        data.course_id,
        data.user_id,
    )

    if not enrollment:
        raise HTTPException(
            detail="Can't get enrollment by course and user", status_code=404
        )
    if enrollment.statement_id:
        statement = await cmi_statement_service.update_statement(
            enrollment.statement_id, data.statement
        )
        return CMIStatementRead(
            course=CMICoursesBase.from_orm(enrollment.course),
            user=UserRead.from_orm(enrollment.user),
            statement=CMIStatementBase.from_orm(statement),
        )
    else:
        statement_obj = await cmi_statement_service.create(data.statement)
        enrollment_obj = await cmi_statement_service.set_statement(
            statement_obj, enrollment
        )
        return CMIStatementRead(
            course=CMICoursesBase.from_orm(enrollment_obj.course),
            user=UserRead.from_orm(enrollment_obj.user),
            statement=CMIStatementBase.from_orm(statement_obj),
        )


@statement_router.get(
    "/all", response_model=list[CMIStatementRead], name="statements:get_all_statements"
)
async def get_all_statements(
    cmi_statement_service: CMIStatementService = Depends(CMIStatementService),
):
    """Get all statements"""

    statements = await cmi_statement_service.get_all()
    if not statements:
        raise HTTPException(detail="Statements not found", status_code=404)

    objs = await cmi_statement_service.get_full_objs(statements)
    return objs


@statement_router.get(
    "/{course_id}/{user_id}",
    response_model=CMIStatementBase | dict,
    name="statements:get_statement",
)
async def get_statement(
    course_id: UUID,
    user_id: UUID,
    statement_service: CMIStatementService = Depends(CMIStatementService),
):
    """Get statement by user for course"""

    statement = await statement_service.get_statement(course_id, user_id)

    if not statement:
        return {}

    return statement
