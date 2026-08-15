"""Create the local development admin used by the normal login flow.

Run from backend with DEV_ADMIN_PASSWORD supplied in the local environment:
    $env:DEV_ADMIN_PASSWORD = '<local password>'
    python -m scripts.create_dev_admin
"""

from __future__ import annotations

import os
import sys

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.entities import User

ADMIN_EMAIL = "admin@letrusto.dev"
LEGACY_ADMIN_EMAIL = "admin@letrusto.local"
PREVIOUS_ADMIN_EMAIL = "admin@letrusto.test"


def main() -> int:
    settings = get_settings()
    if settings.APP_ENV != "development":
        print("Refusing to create a development admin outside APP_ENV=development.")
        return 1

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email.in_([ADMIN_EMAIL, LEGACY_ADMIN_EMAIL, PREVIOUS_ADMIN_EMAIL])).first()
        if user:
            if user.role != "admin":
                print("The development admin email already belongs to a non-admin user; no account was changed.")
                return 1
            if user.email in {LEGACY_ADMIN_EMAIL, PREVIOUS_ADMIN_EMAIL}:
                user.email = ADMIN_EMAIL
                db.commit()
                print("Development admin email updated.")
                return 0
            print("Development admin already exists.")
            return 0

        password = os.environ.get("DEV_ADMIN_PASSWORD", "")
        if not password:
            print("DEV_ADMIN_PASSWORD is required; no admin account was changed.")
            return 1

        user = User(
            email=ADMIN_EMAIL,
            password_hash=hash_password(password),
            full_name="LeTrusto Local Admin",
            role="admin",
            is_active=True,
        )
        db.add(user)
        db.commit()
        print("Development admin created.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
