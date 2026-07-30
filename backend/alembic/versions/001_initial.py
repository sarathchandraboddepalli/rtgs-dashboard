"""Initial tables

Revision ID: 001
Revises:
Create Date: 2026-01-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('departments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), unique=True, nullable=False),
        sa.Column('code', sa.String(20), unique=True),
        sa.Column('category', sa.String(50)),
        sa.Column('budget_crores', sa.Float),
        sa.Column('spent_crores', sa.Float, default=0.0),
        sa.Column('pending_files', sa.Integer, default=0),
        sa.Column('avg_file_clearance_days', sa.Float, default=0.0),
        sa.Column('has_anomaly', sa.Boolean, default=False),
        sa.Column('anomaly_reason', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('schemes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id')),
        sa.Column('scheme_type', sa.String(50)),
        sa.Column('district', sa.String(100)),
        sa.Column('total_beneficiaries', sa.Integer, default=0),
        sa.Column('active_beneficiaries', sa.Integer, default=0),
        sa.Column('pending_applications', sa.Integer, default=0),
        sa.Column('avg_pending_days', sa.Float, default=0.0),
        sa.Column('sla_days', sa.Integer, default=30),
        sa.Column('disbursed_crores', sa.Float, default=0.0),
        sa.Column('target_crores', sa.Float, default=0.0),
        sa.Column('completion_pct', sa.Float, default=0.0),
        sa.Column('is_delayed', sa.Boolean, default=False),
        sa.Column('delay_reason', sa.Text),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('kpi_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id')),
        sa.Column('metric_name', sa.String(255)),
        sa.Column('metric_category', sa.String(50)),
        sa.Column('current_value', sa.Float),
        sa.Column('target_value', sa.Float),
        sa.Column('unit', sa.String(20)),
        sa.Column('is_anomalous', sa.Boolean, default=False),
        sa.Column('trend', sa.String(10), default='stable'),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('nl_queries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('raw_query', sa.Text, nullable=False),
        sa.Column('parsed_intent', sa.String(50)),
        sa.Column('parsed_filters', sa.Text),
        sa.Column('result_summary', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

def downgrade() -> None:
    op.drop_table('nl_queries')
    op.drop_table('kpi_metrics')
    op.drop_table('schemes')
    op.drop_table('departments')
