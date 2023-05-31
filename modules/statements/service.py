from uuid import uuid4

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.db import DBSession
from database.session import get_session
from modules.courses.models import CMIEnrollment
from modules.statements.models import CMIStatement


class CMIStatementService:
    model: CMIStatement = CMIStatement

    def __init__(self, session: DBSession = Depends(get_session)):
        self.session = session

    async def get_all(self) -> list[CMIStatement]:
        objs = (
            (
                await self.session.execute(
                    select(self.model).where(self.model.deleted_at.is_(None))
                )
            )
            .scalars()
            .all()
        )

        return objs

    async def create(self, statement: dict) -> CMIStatement:
        """Create statement for User by course

        Args:
            statement (dict): statement data

        Returns:
            CMIStatement: statement object
        """
        statement = CMIStatement(
            id=uuid4(),
            statements=statement,
        )
        self.session.add(statement)
        await self.session.commit()
        await self.session.refresh(statement)

        return statement

    async def set_statement(
        self, statement: CMIStatement, enrollment: CMIEnrollment
    ) -> CMIEnrollment:
        """Set statement for user by course

        Args:
            statement (CMIStatement): Statement object
            enrollment (CMIEnrollment): Enrollment object

        Returns:
            CMIEnrollment: Updated statement object
        """
        enrollment.statement_id = statement.id
        await self.session.commit()
        obj = (
            await self.session.execute(
                select(CMIEnrollment)
                .where(CMIEnrollment.id == enrollment.id)
                .options(
                    selectinload(
                        CMIEnrollment.user,
                    )
                )
                .options(
                    selectinload(
                        CMIEnrollment.course,
                    )
                )
                .options(
                    selectinload(
                        CMIEnrollment.statement,
                    )
                )
            )
        ).scalar()
        return obj

    async def get_full_objs(
        self, statements: CMIStatement
    ) -> list[CMIEnrollment | None]:
        objs = (
            (
                await self.session.execute(
                    select(CMIEnrollment)
                    .where(
                        CMIEnrollment.statement_id.in_(
                            [st.id for st in statements],
                        )
                    )
                    .options(
                        selectinload(
                            CMIEnrollment.user,
                        )
                    )
                    .options(
                        selectinload(
                            CMIEnrollment.course,
                        )
                    )
                    .options(
                        selectinload(
                            CMIEnrollment.statement,
                        )
                    )
                )
            )
            .scalars()
            .all()
        )
        return objs
