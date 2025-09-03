from fastapi import APIRouter, HTTPException, status
from typing import List

from app.dependencies import db_dep, current_user_dep
from app.models.article import Article, ArticleStatus
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse

router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("/", response_model=List[ArticleResponse])
def list_articles(db: db_dep):

    return db.query(Article).filter(Article.status == ArticleStatus.published).all()


@router.post("/create/", response_model=ArticleResponse)
def create_article(article: ArticleCreate, db: db_dep, current_user: current_user_dep):
    new_article = Article(**article.model_dump(), author_id=current_user.id)

    db.add(new_article)
    db.commit()
    db.refresh(new_article)

    return new_article


@router.get("/{article_id}/", response_model=ArticleResponse)
def get_article(article_id: int, db: db_dep, current_user: current_user_dep):
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found.")

    if article.status != ArticleStatus.published and article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to view this article")

    return article


@router.put("/{article_id}/update/", response_model=ArticleResponse)
def update_article(article_id: int, db: db_dep, article_update: ArticleUpdate, current_user: current_user_dep):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found.")
    if article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to update this article")

    for field, value in article_update.model_dump(exclude_unset=True).items():
        setattr(article, field, value)

    db.commit()
    db.refresh(article)

    return article


@router.delete("/{article_id}/delete/", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(article_id: int, db: db_dep, current_user: current_user_dep):
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="you are not the owner of the article")

    db.delete(article)
    db.commit()

    return None