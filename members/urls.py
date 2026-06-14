from django.urls import path
from .views import login_page, logout_page, dashboard_page, dashboard_upper, csv_report, password_reset, generate_otp, reset_password, verify_otp, dashboard_book_data, dashboard_lowest_books, get_member_issue_details, return_fineregister, dashboard_total_activemember, dashboard_total_inactivemember,  librarian_registration_page, member_registration_page, book_registration_page, book_category_registration_page, book_details_page, member_details_page, librarian_details_page, member_update_request, librarian_update_request, book_update_request, member_delete_request, librarian_delete_request, book_delete_request, member_api, finereport, books_api, borrow_records, borrow_returns, borrow_records_register, record_report, return_fineregister

urlpatterns = [
    path("", login_page, name="log_in"),
    path('logout/', logout_page, name='logout'),
    path("dashboard_page/", dashboard_page, name="dashboard_page"),
    path("dashboard_upper/", dashboard_upper, name="dashboard_upper"),
    path("dashboard_book_data/", dashboard_book_data, name="dashboard_book_data"),
    path("dashboard_lowest_books/", dashboard_lowest_books, name="dashboard_lowest_books"),
    path("dashboard_total_activemember/", dashboard_total_activemember, name="dashboard_total_activemember"),
    path("dashboard_total_inactivemember/", dashboard_total_inactivemember, name="dashboard_total_inactivemember"),


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



    path("records/", borrow_records, name="records"),
    path("records_register/", borrow_records_register, name="records_register"),
    path("record_report/", record_report, name="record_report"),

    path("returns/", borrow_returns, name="returns"),
    path("fine_report/", finereport, name="finereport"),
    path("return_fineregister/", return_fineregister, name="return_fineregister"),
    path("get_member_issue_details/", get_member_issue_details, name="get_member_issue_details"),
    


    path("export_csv/", csv_report, name="export_csv"),



    path("password_reset/", password_reset, name="password_reset"),
    path("generate_otp/", generate_otp, name="generate_otp"),
    path("verify_otp/", verify_otp, name="verify_otp"),
    path("reset_password/", reset_password, name="reset_password"),




    # ========================================> REST APIs <========================================
    path("member/", member_api, name="member"),
    path("member/<int:id>/", member_api),
    path("book/", books_api, name="book"),
    path("books/<int:id>/", books_api),

]
