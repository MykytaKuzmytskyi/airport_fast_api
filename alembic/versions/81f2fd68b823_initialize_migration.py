"""Initialize migration

Revision ID: 81f2fd68b823
Revises: 
Create Date: 2023-11-27 01:46:16.491525

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81f2fd68b823'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('aircraft_type',
    sa.Column('wtc', sa.String(length=1), nullable=False, comment='Wake Turbulence Categories'),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('wtc'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_aircraft_type_wtc'), 'aircraft_type', ['wtc'], unique=False)
    op.create_table('airport',
    sa.Column('airport_code', sa.String(length=3), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('closets_big_city', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('airport_code'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_airport_airport_code'), 'airport', ['airport_code'], unique=False)
    op.create_table('crew',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('first_name', 'last_name', name='unique_crew_first_name_last_name')
    )
    op.create_index(op.f('ix_crew_id'), 'crew', ['id'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    op.create_table('aircraft',
    sa.Column('aircraft_code', sa.String(length=10), nullable=False),
    sa.Column('model', sa.String(length=255), nullable=True),
    sa.Column('range', sa.Integer(), nullable=True),
    sa.Column('rows', sa.Integer(), nullable=True),
    sa.Column('seats_in_row', sa.Integer(), nullable=True),
    sa.Column('aircraft_type_wtc', sa.String(length=1), nullable=True),
    sa.ForeignKeyConstraint(['aircraft_type_wtc'], ['aircraft_type.wtc'], ),
    sa.PrimaryKeyConstraint('aircraft_code'),
    sa.UniqueConstraint('model')
    )
    op.create_index(op.f('ix_aircraft_aircraft_code'), 'aircraft', ['aircraft_code'], unique=False)
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_id'), 'order', ['id'], unique=False)
    op.create_table('route',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('distance', sa.Integer(), nullable=True),
    sa.Column('source_airport_code', sa.String(length=3), nullable=False),
    sa.Column('destination_airport_code', sa.String(length=3), nullable=False),
    sa.ForeignKeyConstraint(['destination_airport_code'], ['airport.airport_code'], ),
    sa.ForeignKeyConstraint(['source_airport_code'], ['airport.airport_code'], ),
    sa.PrimaryKeyConstraint('id', 'source_airport_code', 'destination_airport_code'),
    sa.UniqueConstraint('source_airport_code', 'destination_airport_code', name='unique_route_source_destination')
    )
    op.create_index(op.f('ix_route_id'), 'route', ['id'], unique=True)
    op.create_table('flight',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('route_id', sa.Integer(), nullable=True),
    sa.Column('aircraft_code', sa.String(length=10), nullable=False),
    sa.Column('departure_time', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('arrival_time', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['aircraft_code'], ['aircraft.aircraft_code'], ),
    sa.ForeignKeyConstraint(['route_id'], ['route.id'], ),
    sa.PrimaryKeyConstraint('id', 'aircraft_code')
    )
    op.create_index(op.f('ix_flight_id'), 'flight', ['id'], unique=False)
    op.create_table('flight_crew',
    sa.Column('flight_id', sa.Integer(), nullable=True),
    sa.Column('crew_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['crew_id'], ['crew.id'], ),
    sa.ForeignKeyConstraint(['flight_id'], ['flight.id'], )
    )
    op.create_table('ticket',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('row', sa.Integer(), nullable=True),
    sa.Column('seat', sa.Integer(), nullable=True),
    sa.Column('flight_id', sa.Integer(), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['flight_id'], ['flight.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('row', 'seat', 'flight_id', name='unique_ticket')
    )
    op.create_index(op.f('ix_ticket_id'), 'ticket', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_ticket_id'), table_name='ticket')
    op.drop_table('ticket')
    op.drop_table('flight_crew')
    op.drop_index(op.f('ix_flight_id'), table_name='flight')
    op.drop_table('flight')
    op.drop_index(op.f('ix_route_id'), table_name='route')
    op.drop_table('route')
    op.drop_index(op.f('ix_order_id'), table_name='order')
    op.drop_table('order')
    op.drop_index(op.f('ix_aircraft_aircraft_code'), table_name='aircraft')
    op.drop_table('aircraft')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_crew_id'), table_name='crew')
    op.drop_table('crew')
    op.drop_index(op.f('ix_airport_airport_code'), table_name='airport')
    op.drop_table('airport')
    op.drop_index(op.f('ix_aircraft_type_wtc'), table_name='aircraft_type')
    op.drop_table('aircraft_type')
    # ### end Alembic commands ###
