from sqlalchemy import ForeignKey, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import Enum as SQLAlchemyEnum

from app.database import Base

class ArticleStatus(enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ArticleStatus] = mapped_column(SQLAlchemyEnum(ArticleStatus, name="article_status"), default=ArticleStatus.draft, nullable=False, create_constraint=True)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    author = relationship("User", back_populates="articles")