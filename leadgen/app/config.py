from dataclasses import dataclass
from pathlib import Path
import os


@dataclass
class Settings:
    database_path: Path
    daily_limit: int = 20
    founder_name: str = "Your Name"


def get_settings() -> Settings:
    root = Path(__file__).resolve().parents[1]
    database_path = Path(os.getenv("LEADGEN_DATABASE_PATH", str(root / "data" / "leadgen.sqlite3")))
    return Settings(
        database_path=database_path,
        daily_limit=max(1, int(os.getenv("LEADGEN_DAILY_LIMIT", "20"))),
        founder_name=os.getenv("LEADGEN_FOUNDER_NAME", "Your Name"),
    )
