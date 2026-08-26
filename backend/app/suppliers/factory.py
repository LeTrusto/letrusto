"""Supplier adapter factory — builds the configured adapter from env vars."""

from __future__ import annotations

from app.core.config import get_settings
from app.suppliers.base import SupplierAdapter
from app.suppliers.adapters.cj_adapter import CJAdapter
from app.suppliers.adapters.printful_adapter import PrintfulAdapter


def build_supplier_adapter(provider: str | None = None) -> SupplierAdapter:
    """Return an adapter instance for the configured supplier.

    Currently only CJ is implemented. The architecture supports future adapters
    without changing callers.
    """
    settings = get_settings()
    name = (provider or getattr(settings, "SUPPLIER_PROVIDER", "cj")).lower()

    if name == "cj":
        api_key = getattr(settings, "CJ_API_KEY", "")
        if not api_key:
            raise ValueError("CJ_API_KEY environment variable is not set")
        return CJAdapter(api_key=api_key)

    if name == "printful":
        api_key = getattr(settings, "PRINTFUL_API_KEY", "")
        if not api_key:
            raise ValueError("PRINTFUL_API_KEY environment variable is not set")
        return PrintfulAdapter(api_key=api_key)

    raise ValueError(f"Unknown supplier provider: {name}")
