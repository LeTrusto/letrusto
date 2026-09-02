import csv
from types import SimpleNamespace
from decimal import Decimal
from uuid import uuid4
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.core.config import Settings
from app.models.entities import User
from app.schemas.digital_products import DigitalPaymentVerification
from app.services.digital_product_service import ASSET_ROOT, PRODUCTS, DigitalProductService


class ScalarDB:
    def __init__(self, value):
        self.value = value

    def scalar(self, _statement):
        return self.value


def service(db) -> DigitalProductService:
    return DigitalProductService(db, Settings(RAZORPAY_KEY_ID="key", RAZORPAY_KEY_SECRET="secret"))


def test_product_catalog_rejects_unknown_and_traversal_slugs():
    product_service = service(ScalarDB(None))

    for slug in ("missing", "../small-business-finance-pricing-toolkit", "small-business-finance-pricing-toolkit/../../secret"):
        with pytest.raises(HTTPException) as error:
            product_service._product(slug)
        assert error.value.status_code == 404


def test_download_requires_an_entitlement():
    product_service = service(ScalarDB(None))

    with pytest.raises(HTTPException) as error:
        product_service.download_path(User(id=uuid4()), "small-business-finance-pricing-toolkit")

    assert error.value.status_code == 403
    assert "filesystem" not in str(error.value.detail).lower()


def test_freelancer_toolkit_is_an_allowlisted_product():
    product_service = service(ScalarDB(None))

    product = product_service._product("freelancer-rate-project-pricing-toolkit")

    assert product == {"amount": Decimal("399.00"), "currency": "INR", "filename": "freelancer-rate-project-pricing-toolkit.csv"}


def test_client_work_workbook_is_an_allowlisted_product():
    product_service = service(ScalarDB(None))

    product = product_service._product("freelancer-agency-client-work-workbook")

    assert product == {"amount": Decimal("599.00"), "currency": "INR", "filename": "freelancer-agency-client-work-workbook.csv"}


def test_client_work_workbook_contains_linked_quote_and_profitability_formulas():
    with (ASSET_ROOT / "freelancer-agency-client-work-workbook.csv").open(newline="", encoding="utf-8") as handle:
        parsed_rows = list(csv.DictReader(handle))

    assert parsed_rows
    assert all(None not in row for row in parsed_rows)
    rows = {row["Field"]: row["Input / Example"] for row in parsed_rows}

    assert rows["Base quote"] == "=C22*C23"
    assert rows["Recommended quote"] == "=C25+C26"
    assert rows["Total project cost"] == "=C53*C54+C55"
    assert rows["Profit margin %"] == "=IF(C52=0,0,C57/C52*100)"


def test_all_allowlisted_assets_exist_outside_public_assets():
    public_root = Path(__file__).resolve().parents[2] / "frontend" / "public"

    for product in PRODUCTS.values():
        asset = ASSET_ROOT / str(product["filename"])
        assert asset.is_file()
        assert public_root not in asset.parents


def test_verified_attempt_rejects_replayed_callback_with_different_payment():
    attempt = SimpleNamespace(status="VERIFIED", provider_payment_id="pay_original")
    product_service = service(ScalarDB(attempt))

    with pytest.raises(HTTPException) as error:
        product_service.verify_payment(
            User(id=uuid4()),
            "small-business-finance-pricing-toolkit",
            DigitalPaymentVerification(
                razorpay_order_id="order_original",
                razorpay_payment_id="pay_replayed",
                razorpay_signature="signature",
            ),
        )

    assert error.value.status_code == 409
