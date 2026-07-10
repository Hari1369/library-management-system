# from datetime import date
# import psycopg2
# import psycopg2.extras
# import os

# conn = psycopg2.connect(
#     dbname=os.environ["POSTGRES_DB"],
#     user=os.environ["POSTGRES_USER"],
#     password=os.environ["POSTGRES_PASSWORD"],
#     host=os.environ["DB_HOST"],
#     port=os.environ["DB_PORT"],
# )

# # conn = psycopg2.connect(
# #    dbname="library_db",
# #    user="quantumd",
# #    password="admlqq",
# #    host="localhost",
# #    port="5432"
# # )

# cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# cur.execute("select * from issue_maintanence;")
# issue_maintanence = cur.fetchall()
# def run():
#     # ========================> DECLARATION
#     today = date.today()
#     fine_per_day = 10
#     # ========================> DECLARATION

#     for row in issue_maintanence:
#         maintanence_id = row["id"]
#         maintanence_book_id = row["book_id"]
#         maintanence_member_id = row["member_id"]
#         maintanence_librarian_id = row["librarian_id"]
#         maintanence_issue_date = row["issue_date"]
#         maintanence_due_date = row["due_date"]
#         maintanence_status = row["status"] 
#         maintanence_book_number = row["books_number"]

#         cur.execute("SELECT * FROM book_details WHERE id = %s;", (maintanence_book_id,))
#         book = cur.fetchone()
#         book_isbn = book["isbn"] if book else None
#         book_title = book["title"] if book else None
#         book_author = book["author"] if book else None
#         book_total_copies = book["total_copies"] if book else None
#         book_available_copies = book["available_copies"] if book else None
#         book_category_id = book["category_id"] if book else None
#         book_is_active = book["is_active"] if book else None
#         book_created_at = book["created_at"] if book else None
#         book_publication_year = book["publication_year"] if book else None

#         cur.execute("SELECT * FROM librarian_details WHERE id = %s;", (maintanence_librarian_id,))
#         librarian = cur.fetchone()
#         librarian_username = librarian["username"] if librarian else None
#         librarian_password = librarian["password"] if librarian else None
#         librarian_name = librarian["name"] if librarian else None
#         librarian_surname = librarian["surname"] if librarian else None
#         librarian_email = librarian["email"] if librarian else None
#         librarian_phone_number = librarian["phone_number"] if librarian else None
#         librarian_address = librarian["address"] if librarian else None
#         librarian_is_active = librarian["is_active"] if librarian else None
#         librarian_created_at = librarian["created_at"] if librarian else None
#         librarian_is_shown = librarian["is_shown"] if librarian else None

#         cur.execute("SELECT * FROM member_detail WHERE id = %s;", (maintanence_member_id,))
#         member = cur.fetchone()
#         member_firstname = member["first_name"] if member else None
#         member_lastname = member["last_name"] if member else None
#         member_email = member["email"] if member else None
#         member_phone_number = member["phone_number"] if member else None
#         member_address = member["address"] if member else None
#         member_membership_date = member["membership_date"] if member else None
#         member_created_at = member["created_at"] if member else None



#         # print("=================================> ISSUE MAINTANENCE")
#         # print("MAINTANANCE ID               : ", maintanence_id)
#         # print("MAINTANANCE BOOK ID          : ", maintanence_book_id)
#         # print("MAINTANANCE MEMBER ID        : ", maintanence_member_id)
#         # print("MAINTANANCE LIBRARIAN ID     : ", maintanence_librarian_id)
#         # print("MAINTANANCE ISSUE DATE       : ", maintanence_issue_date)
#         # print("MAINTANANCE DUE DATE         : ", maintanence_due_date)
#         # print("MAINTANANCE STATUS           : ", maintanence_status)
#         # print("MAINTANANCE BOOK NUMBER      : ", maintanence_book_number)

#         # print("=================================> BOOK DETAILS")
#         # print("BOOK ISBN                :   ", book_isbn)
#         # print("BOOK TITLE               :   ", book_title)
#         # print("BOOK AUTHOR              :   ", book_author)
#         # print("BOOK TOTAL COPIES        :   ", book_total_copies)
#         # print("BOOK AVAILABLE COPIES    :   ", book_available_copies)
#         # print("BOOK CATEGORY ID         :   ", book_category_id)
#         # print("BOOK ACTIVE              :   ", book_is_active)
#         # print("BOOK CREATED AT          :   ", book_created_at)

#         # print("=================================> LIBRARIAN DETAILS")
#         # print("LIBRARIAN NAME           :   ", member_firstname)
#         # print("LIBRARIAN PASSWORD       :   ", librarian_password)
#         # print("LIBRARIAN NAME           :   ", librarian_name)
#         # print("LIBRARIAN SURNAME        :   ", librarian_surname)
#         # print("LIBRARIAN EMAIl          :   ", librarian_email)
#         # print("LIBRARIAN PHONE NUMBER   :   ", librarian_phone_number)
#         # print("LIBRARIAN ADDRESS        :   ", librarian_address)
#         # print("LIBRARIAN ACTIVE         :   ", librarian_is_active)
#         # print("LIBRARIAN SHOWN          :   ", librarian_is_shown)
#         # print("LIBRARIAN CREATE AT      :   ", librarian_created_at)

#         # print("=================================> MEMBER DETAILS")
#         # print("MEMBER USERNAME          :   ", member_firstname)
#         # print("MEMBER EMAIL             :   ", member_email)
#         # print("MEMBER PHONE NUMBER      :   ", member_phone_number)
#         # print("MEMBER ADDRESS           :   ", member_address)
#         # print("MEMBER MEMBERSHIP DATE   :   ", member_membership_date)
#         # print("MEMBER CREATED AT        :   ", member_created_at)

#         due_date = maintanence_due_date.date()
#         if maintanence_status == "issued" and due_date < today:
#             overdue_days  = (today - due_date).days
#             fine_amount   = overdue_days * fine_per_day

#             # print(f"MEMBER USERNAME : {member_firstname}")
#             # print(f"OVER-DUE-DAYS   : {overdue_days}")
#             # print(f"FINE DAYS       : {fine_amount}")
#             # print("MAINTANANCE BOOK ID          : ", maintanence_book_id)
#             # print("MAINTANANCE MEMBER ID        : ", maintanence_member_id)
#             # print("MAINTANANCE LIBRARIAN ID     : ", maintanence_librarian_id)
#             # print("MAINTANANCE BOOK NUMBER      : ", maintanence_book_number)

#             # library_test=# select * from fine_maintanence;
#             # id | fine_cost | paid_cost | is_paid | paid_time | created_at | updated_at | book_id | librarian_id | is_return | member_id | books_number
#             # ----+-----------+-----------+---------+-----------+------------+------------+---------+--------------+-----------+-----------+--------------

#             cur.execute("""
#                 INSERT INTO fine_maintanence (
#                     fine_cost,
#                     created_at,
#                     book_id,
#                     librarian_id,
#                     is_return,
#                     member_id,
#                     books_number,
#                     paid_cost,
#                     is_paid,
#                     paid_time,
#                     updated_at,
#                     overdue_date
#                 )
#                 VALUES (%s, NOW(), %s, %s, FALSE, %s, %s, 0, FALSE, NULL, NOW(), %s)
#             """, (
#                 fine_amount,
#                 maintanence_book_id,
#                 maintanence_librarian_id,
#                 maintanence_member_id,
#                 maintanence_book_number,
#                 due_date
#             ))
#             conn.commit()
#             print("ROWS INSERTED:", cur.rowcount)
                
#         # if maintanence_due_date < today:
#         #     cur.execute("SELECT * FROM fine_maintanence WHERE member_id = %s;", (maintanence_book_id,))
#         #     fine_maintanence = cur.fetchone()
#         #     fine_maintanence_fine_cost = fine_maintanence["name"] if fine_maintanence else None
#         #     fine_maintanence_paid_cost = fine_maintanence["paid_cost"] if fine_maintanence else None
#         #     fine_maintanence_is_paid = fine_maintanence["is_paid"] if fine_maintanence else None
#         #     fine_maintanence_book_id = fine_maintanence["book_id"] if fine_maintanence else None
#         #     fine_maintanence_librarian_id = fine_maintanence["librarian_id"] if fine_maintanence else None
#         #     fine_maintanence_member_id = fine_maintanence["member_id"] if fine_maintanence else None
#         #     fine_maintanence_books_number = fine_maintanence["books_number"] if fine_maintanence else None
#         #     print("=================================> FINE MAINTANENCE DETAILS")
#         #     print("FINE MAINTANANCE FINE NAME           :   ", fine_maintanence_fine_cost)
#         #     print("FINE MAINTANANCE PAID COST           :   ", fine_maintanence_paid_cost)
#         #     print("FINE MAINTANANCE IS PAID             :   ", fine_maintanence_is_paid)
#         #     print("FINE MAINTANANCE BOOK ID             :   ", fine_maintanence_book_id)
#         #     print("FINE MAINTANANCE LIBRARIAN ID        :   ", fine_maintanence_librarian_id)
#         #     print("FINE MAINTANANCE MEMBER ID           :   ", fine_maintanence_member_id)
#         #     print("FINE MAINTANANCE BOOKS NUMBER        :   ", fine_maintanence_books_number)
#         #     print("EXCEEDED")
#         # else:
#         #     print("NOT EXCEDED")



# cur.close()
# conn.close()

from datetime import date
import os

import psycopg2
import psycopg2.extras


def get_connection():
    return psycopg2.connect(
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
    )


def run():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute("SELECT * FROM issue_maintanence;")
        issue_maintanence = cur.fetchall()

        today = date.today()
        fine_per_day = 10

        for row in issue_maintanence:

            maintanence_book_id = row["book_id"]
            maintanence_member_id = row["member_id"]
            maintanence_librarian_id = row["librarian_id"]
            maintanence_due_date = row["due_date"]
            maintanence_status = row["status"]
            maintanence_book_number = row["books_number"]

            cur.execute(
                "SELECT * FROM book_details WHERE id=%s;",
                (maintanence_book_id,)
            )
            book = cur.fetchone()

            cur.execute(
                "SELECT * FROM librarian_details WHERE id=%s;",
                (maintanence_librarian_id,)
            )
            librarian = cur.fetchone()

            cur.execute(
                "SELECT * FROM member_detail WHERE id=%s;",
                (maintanence_member_id,)
            )
            member = cur.fetchone()

            due_date = maintanence_due_date.date()

            if maintanence_status == "issued" and due_date < today:

                overdue_days = (today - due_date).days
                fine_amount = overdue_days * fine_per_day

                cur.execute("""
                    INSERT INTO fine_maintanence(
                        fine_cost,
                        created_at,
                        book_id,
                        librarian_id,
                        is_return,
                        member_id,
                        books_number,
                        paid_cost,
                        is_paid,
                        paid_time,
                        updated_at,
                        overdue_date
                    )
                    VALUES(
                        %s,
                        NOW(),
                        %s,
                        %s,
                        FALSE,
                        %s,
                        %s,
                        0,
                        FALSE,
                        NULL,
                        NOW(),
                        %s
                    )
                """, (
                    fine_amount,
                    maintanence_book_id,
                    maintanence_librarian_id,
                    maintanence_member_id,
                    maintanence_book_number,
                    due_date
                ))

        conn.commit()

    finally:
        cur.close()
        conn.close()