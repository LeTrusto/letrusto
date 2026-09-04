import zipfile
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
from app.api.v1.endpoints.digital_products import download_product


class ScalarDB:
    def __init__(self, value):
        self.value = value

    def scalar(self, _statement):
        return self.value

    def commit(self):
        pass


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


def test_fulfillment_test_download_returns_a_protected_zip():
    user = User(id=uuid4(), role="admin")
    entitlement = SimpleNamespace(download_count=0, last_downloaded_at=None)
    response = download_product("letrusto-fulfillment-test-toolkit", user, ScalarDB(entitlement))

    assert response.status_code == 200
    assert response.media_type == "application/zip"
    assert response.headers["content-disposition"].endswith('filename="letrusto-fulfillment-test-toolkit.zip"')
    with zipfile.ZipFile(ASSET_ROOT / "letrusto-fulfillment-test-toolkit.zip") as package:
        assert package.testzip() is None
        names = package.namelist()
        entries = [package.getinfo(name) for name in names]
        assert sum(entry.file_size for entry in entries) > 1_000_000
        assert any(name.startswith("WORKBOOKS/") and name.endswith(".xlsx") for name in names)
        assert any(name.startswith("GUIDES/") and name.endswith(".pdf") for name in names)
        assert any(name.startswith("TEMPLATES/") and name.endswith(".docx") for name in names)


def test_fulfillment_test_download_remains_protected_for_non_admin_without_entitlement():
    with pytest.raises(HTTPException) as error:
        download_product("letrusto-fulfillment-test-toolkit", User(id=uuid4(), role="customer"), ScalarDB(None))

    assert error.value.status_code == 404


def test_freelancer_toolkit_is_an_allowlisted_product():
    product_service = service(ScalarDB(None))

    product = product_service._product("freelancer-rate-project-pricing-toolkit")

    assert product == {"amount": Decimal("99.00"), "currency": "INR", "filename": "LETRUSTO-FREELANCER-KIT-INR99.zip"}


def test_client_work_workbook_is_an_allowlisted_product():
    product_service = service(ScalarDB(None))

    product = product_service._product("freelancer-agency-client-work-workbook")

    assert product == {"amount": Decimal("299.00"), "currency": "INR", "filename": "LETRUSTO-CLIENT-KIT-INR299.zip"}


def test_client_work_bundle_contains_customer_package_structure():
    with zipfile.ZipFile(ASSET_ROOT / "LETRUSTO-CLIENT-KIT-INR299.zip") as package:
        names = package.namelist()

    assert "WORKBOOKS/freelancer-agency-client-work-workbook.xlsx" in names
    assert any(name.startswith("GUIDES/") and name.endswith(".pdf") for name in names)
    assert sum(name.startswith("TEMPLATES/") and name.endswith(".docx") for name in names) >= 20


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
