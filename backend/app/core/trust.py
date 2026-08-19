TRUST_CLAIM_STATUSES = ("UNVERIFIED", "PENDING", "VERIFIED", "REJECTED", "EXPIRED")
TRUST_VERIFICATION_METHODS = (
    "SUPPLIER_DOCUMENT",
    "MANUFACTURER_DOCUMENT",
    "CERTIFICATION",
    "TEST_REPORT",
    "INTERNAL_REVIEW",
    "CUSTOMER_FEEDBACK",
    "SYSTEM_REVIEW",
    "OTHER",
)

TRUST_VERIFICATION_METHOD_LABELS = {
    "SUPPLIER_DOCUMENT": "Supplier documentation reviewed",
    "MANUFACTURER_DOCUMENT": "Manufacturer documentation reviewed",
    "CERTIFICATION": "Certification reviewed",
    "TEST_REPORT": "Test report reviewed",
    "INTERNAL_REVIEW": "LeTrusto internal review",
    "CUSTOMER_FEEDBACK": "Customer feedback reviewed",
    "SYSTEM_REVIEW": "LeTrusto system review",
    "OTHER": "Supporting evidence reviewed",
}
TRUST_AUDIT_EVENTS = (
    "CLAIM_CREATED",
    "CLAIM_UPDATED",
    "EVIDENCE_CREATED",
    "EVIDENCE_UPDATED",
    "EVIDENCE_ATTACHED",
    "VERIFICATION_CREATED",
)
