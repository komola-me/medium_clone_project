from starlette_admin.contrib.sqla import Admin

from app.database import engine
from app.models.user import User
from app.models.article import Article
from app.admin.auth import JSONAuthProvider
from app.admin.views import UserAdminView, ArticleAdminView

admin = Admin(
    engine=engine, title="Medium Admin", base_url="/admin", auth_provider=JSONAuthProvider(login_path="/login", logout_path="/logout")
)

admin.add_view(UserAdminView(User, icon="fa fa-user"))
admin.add_view(ArticleAdminView(Article, icon="fa fa-book"))