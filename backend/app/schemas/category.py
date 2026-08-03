from pydantic import BaseModel


class CategoryDTO(BaseModel):
    id: int
    name: str
    slug: str
    parent_slug: str | None = None
    icon: str | None = None
    position: int = 0


class CategoryTreeNode(BaseModel):
    id: int
    name: str
    slug: str
    icon: str | None = None
    position: int = 0
    children: list["CategoryTreeNode"] = []

CategoryTreeNode.model_rebuild()


class CategoriesResponse(BaseModel):
    items: list[CategoryDTO]


class CatalogTreeResponse(BaseModel):
    tree: list[CategoryTreeNode]
