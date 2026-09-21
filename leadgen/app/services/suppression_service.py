def is_suppressed(lead: dict) -> bool:
    return bool(lead.get("do_not_contact")) or lead.get("status") == "DO_NOT_CONTACT"
