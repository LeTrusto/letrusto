from dataclasses import dataclass
from datetime import datetime
from typing import Any

STATUSES = ["NEW", "RESEARCHING", "QUALIFIED", "READY_TO_CONTACT", "CONTACTED", "FOLLOW_UP_1", "FOLLOW_UP_2", "REPLIED", "INTERESTED", "TRIAL", "INSTALLED", "PAID", "NOT_INTERESTED", "DO_NOT_CONTACT", "BAD_LEAD", "NO_RESPONSE", "CLOSED"]
SOURCES = ["LINKEDIN_MANUAL", "GOOGLE", "COMPANY_WEBSITE", "EXPO", "EVENT_DIRECTORY", "REFERRAL", "OTHER"]

FIELDS = ["company_name", "website", "contact_name", "contact_role", "business_email", "country", "city", "niche", "linkedin_url", "source", "source_url", "review_signal", "review_count_signal", "social_proof_signal", "why_fit", "lead_score", "lead_grade", "status", "email_status", "last_contacted_at", "next_followup_at", "reply_status", "reply_date", "trial_status", "trial_date", "installation_status", "installation_date", "paid_status", "paid_date", "notes", "do_not_contact", "created_at", "updated_at"]

@dataclass
class Lead:
    values: dict[str, Any]

    def __getattr__(self, name: str) -> Any:
        try:
            return self.values[name]
        except KeyError as exc:
            raise AttributeError(name) from exc
