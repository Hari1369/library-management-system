from django.urls import path
from .views import log_in_page, librarian_registration_page, member_api

urlpatterns = [
    path("", log_in_page, name="log_in"),
    path("librarian_registration/", librarian_registration_page, name="librarian_registration"),






    # ========================================> REST APIs <========================================
    path("member/", member_api, name="member"),
]
