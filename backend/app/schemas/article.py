from pydantic import BaseModel


class ArticleDTO(BaseModel):
    id: int
    slug: str
    title: str
    excerpt: str
    content: str
    category: str
    meta_title: str | None
    meta_description: str | None
    view_count: int
    created_at: str


class ArticleListDTO(BaseModel):
    id: int
    slug: str
    title: str
    excerpt: str
    category: str
    created_at: str


class ArticleListResponse(BaseModel):
    items: list[ArticleListDTO]
    total: int


class ArticleCreateRequest(BaseModel):
    slug: str
    title: str
    excerpt: str
    content: str
    category: str = "guide"
    meta_title: str | None = None
    meta_description: str | None = None
    is_published: bool = False
