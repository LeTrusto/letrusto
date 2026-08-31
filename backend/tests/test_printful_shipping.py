from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from app.models.entities import PrintfulShippingRate, Product
from app.schemas.admin_products import PrintfulShippingUpdate
from app.services.printful_shipping_service import PrintfulShippingService, region_for_country


def shipping_product() -> Product:
    return Product(id=uuid4(), slug="hoodie", name="Unisex Hoodie", description="Hoodie", supplier="printful")


def configured_rates() -> list[PrintfulShippingRate]:
    values = {"US": ("8.79", "2.50"), "GB": ("7.29", "2.40"), "EU": ("7.29", "2.40"), "CA": ("10.59", "2.35"), "AU_NZ": ("12.49", "2.25"), "JP": ("7.89", "2.60"), "BR": ("17.69", "8.00"), "WORLDWIDE": ("17.69", "8.00")}
    now = datetime.now(timezone.utc)
    country_codes = {"EU": ["DE", "FR"], "AU_NZ": ["AU", "NZ"], "WORLDWIDE": ["CH"]}
    return [PrintfulShippingRate(source="printful", rate_source="PRINTFUL_PUBLISHED", destination_region=region, category_key="hoodies-sweatshirts", country_codes=country_codes.get(region, [region]), shipping_method="Standard", single_product_rate=Decimal(single), additional_product_rate=Decimal(additional), currency="USD", effective_at=now, updated_at=now, active=True) for region, (single, additional) in values.items()] + [PrintfulShippingRate(source="printful", rate_source="LETRUSTO_ESTIMATE", destination_region="IN", category_key="hoodies-sweatshirts", country_codes=[], shipping_method="Standard", single_product_rate=Decimal("299"), additional_product_rate=Decimal("100"), currency="INR", effective_at=now, updated_at=now, active=True, requires_verification=True)]


def test_printful_hoodie_rates_and_destination_mapping():
    service = PrintfulShippingService(None)  # type: ignore[arg-type]
    service._rows = lambda _: configured_rates()  # type: ignore[method-assign]
    product = shipping_product()

    expected = {"US": "8.79", "GB": "7.29", "DE": "7.29", "CA": "10.59", "AU": "12.49", "NZ": "12.49", "JP": "7.89", "BR": "17.69", "FR": "7.29"}
    for country, rate in expected.items():
        result = service.estimate(product, country)
        assert result["status"] == "AVAILABLE"
        assert result["shipping_price"] == Decimal(rate)

    assert region_for_country("IN") == "IN"
    india = service.estimate(product, "IN")
    assert india["status"] == "AVAILABLE"
    assert india["shipping_price"] == Decimal("299")
    assert india["currency"] == "INR"
    assert india["rate_source"] == "LETRUSTO_ESTIMATE"
    assert india["estimated"] is True


def test_printful_additional_rate_and_review_blockers():
    service = PrintfulShippingService(None)  # type: ignore[arg-type]
    service._rows = lambda _: configured_rates()  # type: ignore[method-assign]
    product = shipping_product()
    assert service.estimate(product, "US", quantity=3)["shipping_price"] == Decimal("13.79")
    assert service.estimate(product, "IN", quantity=2)["shipping_price"] == Decimal("399")
    assert service.estimate(product, "IN", quantity=3)["shipping_price"] == Decimal("499")
    assert service.review(product) == (True, [])

    incomplete = configured_rates()
    incomplete = [row for row in incomplete if row.destination_region != "JP"]
    service._rows = lambda _: incomplete  # type: ignore[method-assign]
    reviewed, blockers = service.review(product)
    assert reviewed is False
    assert "SHIPPING_RATE_MISSING_JP" in blockers


def test_india_estimate_update_requires_inr_rates_and_source():
    payload = PrintfulShippingUpdate(region="IN", currency="INR", rate_source="LETRUSTO_ESTIMATE", single_product_rate=Decimal("299"), additional_product_rate=Decimal("100"), requires_verification=True)

    assert payload.country_codes == []
    assert payload.single_product_rate == Decimal("299")
    assert payload.additional_product_rate == Decimal("100")