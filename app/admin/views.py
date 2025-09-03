from typing import ClassVar
from starlette_admin.contrib.sqla import ModelView

class UserAdminView(ModelView):
    fields: ClassVar[list[str]] = [
        "id",
        "email",
        "username",
        "is_active",
        "is_admin",
        "created_at",
    ]
    exclude_fields_from_list: ClassVar[list[str]] = ["created_at"]
    exclude_fields_from_create: ClassVar[list[str]] = ["created_at"]
    exclude_fields_from_edit: ClassVar[list[str]] = ["created_at"]
    export_fields: ClassVar[list[str]] = [
        "id",
        "email",
        "username",
        "is_active",
        "created_at",
    ]
    export_types: ClassVar[list[str]] = ["csv", "excel", "pdf", "print"]


class ArticleAdminView(ModelView):
    fields: ClassVar[list[str]] = [
        "id", "title", "content", "status"
    ]
    exclude_fields_from_list: ClassVar[list[str]] = []
    exclude_fields_from_create: ClassVar[list[str]] = []
    exclude_fields_from_edit: ClassVar[list[str]] = []
    export_fields: ClassVar[list[str]] = [
        "id", "title", "content",
        "status",
    ]
    export_types: ClassVar[list[str]] = ["csv", "excel", "pdf", "print"]