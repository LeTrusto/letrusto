"""Seed the initial Bengaluru locality options for property listings."""

from collections.abc import Sequence
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260926_54"
down_revision: str | None = "20260923_53"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


LOCALITIES = (
    "Banashankari",
    "Basavanagudi",
    "Bellandur",
    "Benson Town",
    "BTM Layout",
    "Brookefield",
    "HSR Layout",
    "Hebbal",
    "Hennur",
    "Indiranagar",
    "Jayanagar",
    "JP Nagar",
    "Koramangala",
    "Krishnarajapuram",
    "Mahadevapura",
    "Malleshwaram",
    "Marathahalli",
    "Nagarbhavi",
    "Padmanabhanagar",
    "Rajajinagar",
    "Ramamurthy Nagar",
    "Richmond Town",
    "Sarjapur Road",
    "Sanjay Nagar",
    "Shivajinagar",
    "Thanisandra",
    "Uttarahalli",
    "Varthur",
    "Vijayanagar",
    "Whitefield",
    "Yelahanka",
)


def _normalized(value: str) -> str:
    return value.lower().replace(" ", "-")


def upgrade() -> None:
    locations = sa.table(
        "locations",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("parent_id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.String()),
        sa.column("slug", sa.String()),
        sa.column("location_type", sa.String()),
        sa.column("normalized_name", sa.String()),
        sa.column("city_name", sa.String()),
        sa.column("is_active", sa.Boolean()),
    )
    op.bulk_insert(
        locations,
        [
            {
                "id": uuid4(),
                "parent_id": None,
                "name": name.strip(),
                "slug": _normalized(name.strip()),
                "location_type": "LOCALITY",
                "normalized_name": _normalized(name.strip()),
                "city_name": "Bengaluru",
                "is_active": True,
            }
            for name in LOCALITIES
        ],
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM locations WHERE location_type = 'LOCALITY' "
            "AND city_name = 'Bengaluru' AND parent_id IS NULL "
            "AND normalized_name IN :names"
        ).bindparams(sa.bindparam("names", expanding=True)).params(
            names=[_normalized(name.strip()) for name in LOCALITIES]
        )
    )