from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db, get_optional_user
from app.models.entities import Article, User
from app.schemas.article import ArticleDTO, ArticleListResponse, ArticleListDTO, ArticleCreateRequest
from app.schemas.common import MessageResponse
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=ArticleListResponse)
def list_articles(
    category: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> ArticleListResponse:
    q = db.query(Article).filter(Article.is_published.is_(True))
    if category:
        q = q.filter(Article.category == category)
    total = q.count()
    items = q.order_by(Article.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return ArticleListResponse(
        total=total,
        items=[ArticleListDTO(id=a.id, slug=a.slug, title=a.title, excerpt=a.excerpt, category=a.category, created_at=a.created_at.isoformat()) for a in items],
    )


@router.get("/{slug}", response_model=ArticleDTO)
def get_article(slug: str, db: Session = Depends(get_db)) -> ArticleDTO:
    article = db.scalars(select(Article).where(Article.slug == slug, Article.is_published.is_(True))).first()
    if not article:
        raise NotFoundError(f"Article '{slug}' not found")
    # Increment view count
    article.view_count += 1
    db.commit()
    return ArticleDTO(
        id=article.id, slug=article.slug, title=article.title,
        excerpt=article.excerpt, content=article.content,
        category=article.category, meta_title=article.meta_title,
        meta_description=article.meta_description, view_count=article.view_count,
        created_at=article.created_at.isoformat(),
    )


@router.post("", response_model=ArticleDTO, status_code=201)
def create_article(
    payload: ArticleCreateRequest,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ArticleDTO:
    article = Article(**payload.model_dump())
    db.add(article)
    db.commit()
    db.refresh(article)
    return ArticleDTO(
        id=article.id, slug=article.slug, title=article.title,
        excerpt=article.excerpt, content=article.content,
        category=article.category, meta_title=article.meta_title,
        meta_description=article.meta_description, view_count=0,
        created_at=article.created_at.isoformat(),
    )
