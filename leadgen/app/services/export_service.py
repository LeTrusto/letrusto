import csv
import io

FIELDS = ["id", "company_name", "website", "contact_name", "contact_role", "business_email", "country", "city", "niche", "linkedin_url", "source", "source_url", "review_signal", "review_count_signal", "social_proof_signal", "why_fit", "lead_score", "lead_grade", "status", "email_status", "last_contacted_at", "next_followup_at", "reply_status", "reply_date", "trial_status", "trial_date", "installation_status", "installation_date", "paid_status", "paid_date", "notes", "do_not_contact", "created_at", "updated_at"]


def rows_to_csv(rows: list[dict]) -> str:
    fields = FIELDS
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def rows_to_xlsx(rows: list[dict]) -> bytes:
    from openpyxl import Workbook
    from openpyxl.styles import Font

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Leads"
    sheet.append(FIELDS)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    for row in rows:
        sheet.append([row.get(field, "") for field in FIELDS])
    for column_cells in sheet.columns:
        length = max((len(str(cell.value)) for cell in column_cells if cell.value is not None), default=8)
        sheet.column_dimensions[column_cells[0].column_letter].width = min(48, max(10, length + 2))
    sheet.freeze_panes = "A2"
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def parse_csv(text: str) -> list[dict[str, str]]:
    aliases = {"Company": "company_name", "Company Name": "company_name", "Website": "website", "Email": "business_email", "Business Email": "business_email", "Founder": "contact_name", "Founder Name": "contact_name", "Owner": "contact_name", "Contact": "contact_name", "LinkedIn": "linkedin_url", "LinkedIn URL": "linkedin_url", "Country": "country", "Niche": "niche", "Observation": "review_signal", "Why Fit": "why_fit"}
    reader = csv.DictReader(io.StringIO(text))
    leads = []
    for row in reader:
        normalized = {}
        for key, value in row.items():
            normalized[aliases.get(key, key.strip().lower().replace(" ", "_"))] = (value or "").strip()
        if normalized.get("company_name"):
            leads.append(normalized)
    return leads
