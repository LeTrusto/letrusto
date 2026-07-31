from pydantic import BaseModel, Field


class Pagination(BaseModel):
    page: int = Field(ge=1)
    pageSize: int = Field(ge=1)
    totalItems: int = Field(ge=0)
    totalPages: int = Field(ge=1)
    hasNextPage: bool
    hasPreviousPage: bool


class MessageResponse(BaseModel):
    message: str
