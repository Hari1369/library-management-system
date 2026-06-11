from django.urls import path
from .views import login_page, logout_page, dashboard_page, librarian_registration_page, member_registration_page, book_registration_page, book_category_registration_page, book_details_page, member_details_page, librarian_details_page, member_update_request, librarian_update_request, book_update_request, member_delete_request, librarian_delete_request, book_delete_request, member_api, books_api

urlpatterns = [
    path("", login_page, name="log_in"),
    path('logout/', logout_page, name='logout'),
    path("dashboard_page/", dashboard_page, name="dashboard_page"),




    path("librarian_registration/", librarian_registration_page, name="librarian_registration"),
    path("librarian_details/", librarian_details_page, name="librarian_details"),
    path("update_librarian/", librarian_update_request, name="update_librarian"),
    path("librarian_delete/", librarian_delete_request, name="librarian_delete"),


    path("book_registration/", book_registration_page, name="book_registration"),
    path("book_category_registration/", book_category_registration_page, name="book_category_registration"),
    path("book_details/", book_details_page, name="book_details"),
    path("update_book/", book_update_request, name="update_book"),
    path("book_delete/", book_delete_request, name="book_delete"),


    
    path("member_details/", member_details_page, name="member_details"),
    path("member_registration/", member_registration_page, name="member_registration"),
    path("update_member/", member_update_request, name="update_member"),
    path("member_delete/", member_delete_request, name="member_delete"),
    


    # ========================================> REST APIs <========================================
    path("member/", member_api, name="member"),
    path("member/<int:id>/", member_api),
    path("book/", books_api, name="book"),
    path("books/<int:id>/", books_api),

]
