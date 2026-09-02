from pydantic import BaseModel, EmailStr, Field


class FaqItemDTO(BaseModel):
    question: str
    answer: str
    category: str


class FaqListResponse(BaseModel):
    items: list[FaqItemDTO]


class SupportTicketRequest(BaseModel):
    email: EmailStr
    category: str = Field(pattern=r"^(contact|feedback|report_wrong|report_broken|service_enquiry|other)$")
    subject: str = Field(min_length=5, max_length=200)
    body: str = Field(min_length=10, max_length=2000)
    service_slug: str | None = Field(default=None, max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    customer_name: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
    current_website: str | None = Field(default=None, max_length=500)
    timeline: str | None = Field(default=None, max_length=120)
    budget_range: str | None = Field(default=None, max_length=120)


class SupportTicketResponse(BaseModel):
    id: int
    status: str
    message: str
