from pydantic import BaseModel
from typing import Annotated, Optional
from enum import Enum

from app.models.article import ArticleStatus

class ArticleBase(BaseModel):
    title: str
    content: str
    status: ArticleStatus = ArticleStatus.draft


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[ArticleStatus] = None


class ArticleResponse(ArticleBase):
    id: int
    author_id: int

    class Config:
        from_attributes = True
