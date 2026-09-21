from datetime import datetime, timedelta


def next_followup(initial_contact: datetime, step: int) -> datetime:
    return initial_contact + timedelta(days=4 if step == 1 else 10)


def followup_step(status: str) -> int:
    return {"CONTACTED": 1, "FOLLOW_UP_1": 2}.get(status, 0)
