"""baseline

Revision ID: 966de17f903e
Revises:
Create Date: 2026-07-14 13:55:16.763275

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# идентификаторы ревизии, используются Alembic
revision: str = "966de17f903e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Применить изменения схемы."""
    pass


def downgrade() -> None:
    """Откатить изменения схемы."""
    pass
