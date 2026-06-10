from django.urls import path
from .views import log_in_page, librarian_registration_page, member_registration_page, book_registration_page, book_category_registration_page, book_details_page, member_details_page, librarian_details_page

urlpatterns = [
    path("", log_in_page, name="log_in"),
    path("librarian_registration/", librarian_registration_page, name="librarian_registration"),
    path("librarian_details/", librarian_details_page, name="librarian_details"),
    



    path("book_registration/", book_registration_page, name="book_registration"),
    path("book_category_registration/", book_category_registration_page, name="book_category_registration"),
    path("book_details/", book_details_page, name="book_details"),



    
    path("member_details/", member_details_page, name="member_details"),
    path("member_registration/", member_registration_page, name="member_registration"),



    # ========================================> REST APIs <========================================
    # path("member/", member_api, name="member"),
]
