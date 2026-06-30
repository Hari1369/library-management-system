from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Librarian


@admin.register(Librarian)
class LibrarianAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "name",
        "surname",
        "email",
        "phone_number",
        "is_active",
    )

    def save_model(self, request, obj, form, change):
        if "password" in form.changed_data:
            obj.password = make_password(obj.password)

        super().save_model(request, obj, form, change)