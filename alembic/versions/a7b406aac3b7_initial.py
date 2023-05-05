"""initial

Revision ID: a7b406aac3b7
Revises: 
Create Date: 2023-05-05 13:41:31.774252

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a7b406aac3b7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cmi_courses',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('password', sa.VARCHAR(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_cmi_courses'))
    )
    op.create_index(op.f('ix_cmi_courses_id'), 'cmi_courses', ['id'], unique=False)
    op.create_table('cmi_statements',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('statements', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_cmi_statements'))
    )
    op.create_index(op.f('ix_cmi_statements_id'), 'cmi_statements', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('password', sa.VARCHAR(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users'))
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('cmi5_course_users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('statement_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['cmi_courses.id'], name=op.f('fk_cmi5_course_users_course_id_cmi_courses')),
    sa.ForeignKeyConstraint(['statement_id'], ['cmi_statements.id'], name=op.f('fk_cmi5_course_users_statement_id_cmi_statements')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_cmi5_course_users_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_cmi5_course_users'))
    )
    op.create_index(op.f('ix_cmi5_course_users_id'), 'cmi5_course_users', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_cmi5_course_users_id'), table_name='cmi5_course_users')
    op.drop_table('cmi5_course_users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_cmi_statements_id'), table_name='cmi_statements')
    op.drop_table('cmi_statements')
    op.drop_index(op.f('ix_cmi_courses_id'), table_name='cmi_courses')
    op.drop_table('cmi_courses')
    # ### end Alembic commands ###
