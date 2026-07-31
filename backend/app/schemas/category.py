from pydantic import BaseModel


class CategoryDTO(BaseModel):
    id: int
    name: str
    slug: str


class CategoriesResponse(BaseModel):
    items: list[CategoryDTO]
