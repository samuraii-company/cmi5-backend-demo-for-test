from fastapi import APIRouter, Depends, HTTPException

from modules.courses.service import CMICourseService
from modules.statements.schema import CMIStatementRead, CMIStatementsCreate
from modules.statements.service import CMIStatementService

statement_router = APIRouter(tags=["statement"], prefix="/api/statement")


@statement_router.post(
    "",
    response_model=CMIStatementRead,
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

    statement_obj = await cmi_statement_service.create(data.statement)

    enrollment_obj = await cmi_statement_service.set_statement(
        statement_obj, enrollment
    )

    return enrollment_obj


@statement_router.get(
    "/all",
    response_model=list[CMIStatementRead],
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
