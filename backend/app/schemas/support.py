from pydantic import BaseModel, EmailStr, Field


class FaqItemDTO(BaseModel):
    question: str
    answer: str
    category: str


class FaqListResponse(BaseModel):
    items: list[FaqItemDTO]


class SupportTicketRequest(BaseModel):
    email: EmailStr
    category: str = Field(pattern=r"^(contact|feedback|report_wrong|report_broken|other)$")
    subject: str = Field(min_length=5, max_length=200)
    body: str = Field(min_length=10, max_length=2000)


class SupportTicketResponse(BaseModel):
    id: int
    status: str
    message: str
