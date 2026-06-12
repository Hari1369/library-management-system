from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import transaction, IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Librarian, Member, BookDetails, BookCategory, IssueMaintanence, FineMaintanence
from .serializers import LibrarianSerializers, MemberSerializers, BookDetailsSerializers
from .forms import LoginForm, LibrarianFrom, BookCategoryForm, BookForm, MemberFrom
from .decorators import role_required
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime, date
from django.db.models import Sum, Count, Max, Sum
from django.db.models import F
import json



def login_page(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            # ================================>
            print("USERNAME : ", username)
            print("PASSWORD : ", password)
            # ================================>
            user = authenticate(request, username=username, password=password)
            librarian = Librarian.objects.filter(username=username,is_active=True).first()

            if user is not None:
                login(request, user)
                request.session["id"] = user.id
                request.session["username"] = user.username
                if not user.is_active:
                    messages.error(request, "Account disabled.")
                    return render(request, "log_in/log_in.html", {"form": form})
                if user.is_superuser and user.is_staff:
                    request.session["superuser_id"] = user.id
                    request.session["role"] = "super_admin"
                elif librarian:
                    request.session["librarian_id"] = librarian.id
                    request.session["role"] = "librarian"
                else:
                    messages.error(request, "Unauthorized role.")
                    return render(request, "log_in/log_in.html", {"form": form})

                return redirect("dashboard_page")
            else:
                messages.error(request, "Invalid username or password.")
    return render(request, "log_in/log_in.html", {"form": form})


def logout_page(request):
    logout(request)
    return redirect('log_in')

@login_required
@role_required(["super_admin","librarian"])
def dashboard_page(request):
    return render(request, "librarians_dashboard/librarians_dashboard.html")

@login_required
@role_required(["super_admin"])
def librarian_registration_page(request):
    form = LibrarianFrom()
    if request.method == "POST":
        form = LibrarianFrom(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            name = form.cleaned_data["name"].title()
            surname = form.cleaned_data["surname"].title()
            email = form.cleaned_data["email"]
            phone_number = form.cleaned_data["phone_number"]
            address = form.cleaned_data["address"].title()
            is_active = form.cleaned_data["is_active"]

            # ================================>
            print("Username :", username)
            print("Password :", password)
            print("Name     :", name)
            print("Surname  :", surname)
            print("Email    :", email)
            print("Phone    :", phone_number)
            print("Address  :", address)
            print("Active   :", is_active)
            # ================================>

            if User.objects.filter(username=username).exists():
                return HttpResponse("Username already exists", status=409)
                if Librarian.objects.filter(username=username).exists():
                    return HttpResponse("Username already exists Please do active again", status=409)
            try:
                with transaction.atomic():
                    user_insert = User.objects.create_user(
                        username=username,
                        password=password,
                        email=email,
                        first_name=name,
                        last_name=surname,
                        is_active=is_active,
                        is_staff=is_active,
                        is_superuser=False 
                    )                        
                    Librarian.objects.create(
                        username=username,
                        password=password,
                        name=name,
                        surname=surname,
                        email=email,
                        phone_number=phone_number,
                        address=address,
                        is_active=is_active,
                        is_shown=is_active
                    )
                    return render(request, "librarians_registration/librarians_registration.html", {"form": form, "success": "Librarian inserted successfully!"})
            except Exception as e:
                print("FULL ERROR:", e)
                return render(request, "librarians_registration/librarians_registration.html", {"form": form,"error": str(e)})
        return render(request, "librarians_registration/librarians_registration.html", {"form": form})
    return render(request, "librarians_registration/librarians_registration.html", {"form": form})
    

@login_required
@role_required(["super_admin"])
def librarian_details_page(request):
    librarian = Librarian.objects.filter(is_shown=True).order_by('-updated_at')
    user_list = []
    for user in librarian:
        id = user.id
        username = user.username
        password = user.password
        name = user.name.title()
        surname = user.surname.title()
        email = user.email
        phone_number = user.phone_number
        address = user.address
        is_active = user.is_active
        created_at = user.created_at

        # ================================>
        print("ID               : ", id)
        print("USERNAME         : ", username)
        print("PASSWORD         : ", password)
        print("NAME             : ", name)
        print("SURNAME          : ", surname)
        print("EMAIL            : ", email)
        print("PHONE NUMBER     : ", phone_number)
        print("ADDRESS          : ", address)
        print("IS ACTIVE        : ", is_active)
        # ================================>

        user_list.append({
            "id": user.id,
            "username": user.username,
            "password": user.password,
            "name": user.name,
            "surname": user.surname,
            "email": user.email,
            "phone_number": user.phone_number,
            "address": user.address,
            "is_active": user.is_active,
            "created_at": user.created_at,
        })
    return render(request, "librarians_details/librarians_details.html", {"users" : user_list})

@csrf_exempt
def librarian_update_request(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        print("DATA : ", data)
        username = data.get("username")
        password = data.get("password")
        name = data.get("name").title()
        surname = data.get("surname").title()
        email = data.get("email")
        phone = data.get("phone")
        address = data.get("address").title()

        librarian = Librarian.objects.filter(username=username).first()
        user_1 = User.objects.filter(username=username).first()

        if librarian:
            if librarian.password != password:
                if user_1:
                    user_1.is_active = False
                    user_1.save()
                    librarian.password = password
                    librarian.name = name
                    librarian.surname = surname
                    librarian.email = email
                    librarian.phone = phone
                    librarian.address = address
                    librarian.is_active = False
                    librarian.save()
            else:
                librarian.name = name
                librarian.surname = surname
                librarian.email = email
                librarian.phone = phone
                librarian.address = address
                librarian.save()
        else:
            Librarian.objects.create(
                username=username,
                password=password,
                name=name,
                surname=surname,
                email=email,
                phone=phone,
                address=address
            )

        return JsonResponse({
            "status": "success",
            "message": "Data received successfully",
            "received_data": data
        })
    return JsonResponse({
        "status": "error",
        "message": "Something Went Wrong"
    }, status=405)

@csrf_exempt
def librarian_delete_request(request):
    if request.method == "DELETE":
        data = json.loads(request.body)
        username = data.get("username")
        name = data.get("name").title()
        email = data.get("email")
        is_active = str(data.get("is_active")).lower() == "true"

        # ================================>
        print("USERNAME     : ", username)
        print("NAME         : ", name)
        print("EMAIL        : ", email)
        print("IS ACTIVE    : ", is_active)
        # ================================>

        if is_active:
            return JsonResponse({
                "status": "error",
                "message": "Active Librarian cannot be deleted"
            }, status=400)
            
        try:
            librarian = Librarian.objects.get(username=username)
            if librarian.is_active:
                return JsonResponse({
                    "status": "error",
                    "message": "Active Librarian cannot be deleted"
                }, status=400)

            librarian.is_shown = False
            librarian.save()

            return JsonResponse({
                "status": "success",
                "message": "Librarian deleted successfully"
            })

        except Librarian.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Librarian not found"
            }, status=404)

    return JsonResponse({
        "status": "error",
        "message": "Member is already inactive or invalid request"
    }, status=400)


@login_required
@role_required(["super_admin", "librarian"])
def member_registration_page(request):
    form = MemberFrom()
    if request.method == "POST":
        form = MemberFrom(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"].title()
            email = form.cleaned_data["email"]
            phone_number = form.cleaned_data["phone_number"]
            address = form.cleaned_data["address"].title()
            membership_date = form.cleaned_data["membership_date"]
            is_active = form.cleaned_data["is_active"]

            if membership_date < date.today():
                return render(request, "member_registration/member_registration.html", {"form": form, "error": "Membership date cannot be in the past."})

            # ================================>
            print("NAME                 : ",  name)
            print("EMAIL                : ",  email)
            print("PHONE NUMBER         : ",  phone_number)
            print("ADDRESS              : ",  address)
            print("MEMBERSHIP DATE      : ",  membership_date)
            print("ACTIVE               : ",  is_active)
            # ================================>

            if Member.objects.filter(name=name).exists():
                return HttpResponse("Name already exists", status=409)
            
            try:
                with transaction.atomic():
                    member_insert = Member.objects.create(
                        name=name,
                        email=email,
                        phone_number=phone_number,
                        address=address,
                        membership_date=membership_date,
                        is_active=is_active,
                    )                 
                    return render(request, "member_registration/member_registration.html", {"form": form, "success": f"Member {member_insert.name} inserted successfully!"})
            except IntegrityError:
                return render(request, "member_registration/member_registration.html", {"form": form,"error": "Database error occurred. Try again."})
        else:
            print("something went wrong!")
            print(form.errors)
    else:
        form = MemberFrom()
    return render(request, "member_registration/member_registration.html", {"form" : form})

@login_required
@role_required(["super_admin", "librarian"])
def member_details_page(request):
    members = Member.objects.filter(is_active=True)
    member_list = []
    for i in members:
        id = i.id
        name = i.name.title()
        email = i.email
        phone_number = i.phone_number
        address = i.address.title()
        membership_date = i.membership_date.strftime("%d-%m-%Y") if i.membership_date else ""
        is_active = i.is_active
        is_expired = i.is_expired
        created_at = i.created_at

        # ================================>
        print("ID               : ", id)
        print("NAME             : ", name)
        print("EMAIL            : ", email)
        print("PHONE NUMBER     : ", phone_number)
        print("ADDRESS          : ", address)
        print("MEMBERSHIP DATE  : ", membership_date)
        print("ACTIVE           : ", is_active)
        print("EXPIRED          : ", is_expired)
        print("CREATED AT       : ", created_at)
        # ================================>

        member_list.append({
            "id" : id,
            "name" : name,
            "email" : email,
            "phone_number" : phone_number,
            "membership_date": membership_date,
            "is_active" : is_active,
            "is_expired" : is_expired,
            "created_at" : created_at,
        })
    return render(request, "member_details/member_details.html",  {"members": members})

@csrf_exempt
def member_update_request(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        member_id = data.get("id")
        name = data.get("name").title()
        email = data.get("email")
        phone = data.get("phone")
        address = data.get("address")
        membership_date = data.get("membership_date")
        if membership_date:
            membership_date = datetime.strptime(membership_date, "%Y-%m-%d").date()
            
        if membership_date < date.today():
            return render(request, "member_registration/member_registration.html", {"form": form, "error": "Membership date cannot be in the past."})  
        # ================================>
        print("ID                   :", member_id)
        print("NAME                 :", name)
        print("EMAIL                :", email)
        print("PHONE                :", phone)
        print("ADDRESSS             :", address)
        print("MEMBERSHIP DATE      :", membership_date)
        # ================================>

        try:
            member = Member.objects.get(id=member_id)

            member.name = name
            member.email = email
            member.phone_number = phone
            member.address = address
            if membership_date:
                member.membership_date = membership_date

            member.save()

        except Member.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Member not found"
            }, status=404)

        return JsonResponse({
            "status": "success",
            "message": "Data received successfully",
            "received_data": data
        })

    return JsonResponse({
        "status": "error",
        "message": "Something Went Wrong!"
    }, status=405)


@csrf_exempt
def member_delete_request(request):
    if request.method == "DELETE":
        data = json.loads(request.body)
        member_id = data.get("id")
        name = data.get("name").title()
        is_active = data.get("is_active")
        is_active = True if str(is_active).lower() == "true" else False

        # ================================>
        print("ID                   :", member_id)
        print("NAME                 :", name)
        print("ACTIVE               :", is_active)
        # ================================>

        if is_active is True:
            try:
                member = Member.objects.get(id=member_id)
                member.is_active = False
                member.save()
                return JsonResponse({
                    "status": "success",
                    "message": "Member deactivated successfully",
                    "id": member_id,
                    "is_active": member.is_active
                })
            except Member.DoesNotExist:
                return JsonResponse({
                    "error": "Member not found"
                }, status=404)
        return JsonResponse({
            "status": "error",
            "message": "Member is already inactive or invalid request"
        }, status=400)

@login_required
@role_required(["super_admin", "librarian"])
def book_category_registration_page(request):
    form = BookCategoryForm()
    category = BookCategory.objects.all()
    category_list = []
    for choice in category:
        id = choice.id
        choice_value = choice.choice

        # ================================>
        print("ID       : ", id)
        print("CHOICE   : ", choice_value)
        # ================================>

        category_list.append({
            "id" : id,
            "choice" : choice_value
        })
    if request.method == "POST":
        form = BookCategoryForm(request.POST)
        if form.is_valid():
            choice = form.cleaned_data["choice"].title()

            # ================================>
            print("CHOICE : ", choice)
            # ================================>

            if BookCategory.objects.filter(choice=choice).exists():
                return render(request, "book_category_registration/book_category_registration.html", {
                    "form": form,
                    "category_list": category_list,
                    "error": "Category already exists"
                })

            BookCategory.objects.create(choice=choice)
            return redirect("book_category_registration")
            # return render(request, "book_category_registration/book_category_registration.html", {"form": form, "category_list": category_list, "success": "Category Added Successfully!"})
        else:
            print("something went wrong!")
            print(form.errors)
    else:
        return render(request, "book_category_registration/book_category_registration.html", {"form": form, "category_list": category_list})

@login_required
@role_required(["super_admin", "librarian"])
def book_registration_page(request):
    form = BookForm()
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title'].title()
            author = form.cleaned_data['author'].title()
            category = form.cleaned_data['category']
            publication_year = form.cleaned_data['publication_year']
            total_copies = form.cleaned_data['total_copies']
            available_copies = total_copies
            category_id = category.id

            # ================================>
            print("TITLE                : ", title)
            print("AUTOR                : ", author)
            print("CATEGORY             : ", category_id)
            print("PUBLICATION YEAR     : ", publication_year)
            print("TOTAL COPIES         : ", total_copies)
            print("AVAILABLE COPIES     : ", available_copies)
            # ================================>

            if BookDetails.objects.filter(title=title).exists():
                return render(request, "book_registration/add_books.html", {
                    "form": form,
                    "error": "Book is already exists"
                })

            isbn_last = BookDetails.objects.order_by("-id").first()
            if isbn_last is None:
                isbn  = "BOO01"
            else:
                last_number = int(isbn_last.isbn[3:])
                new_number = last_number + 1
                isbn  = f"BOO{new_number:02d}"

            try:
                with transaction.atomic():
                    book_insert = BookDetails.objects.create(
                        isbn=isbn,
                        title=title,
                        author=author,
                        publication_year=publication_year,
                        total_copies=total_copies,
                        available_copies=available_copies,
                        category_id=category_id,
                    )
                    return render(request, "book_registration/add_books.html", {"form": form, "success": f"Book {book_insert.isbn} with Author {book_insert.author} Added Successfully!"})
            except IntegrityError:
                return render(request, "book_registration/add_books.html", {"form": form,"error": "Database error occurred. Try again."})
    return render(request, "book_registration/add_books.html", {"form": form})

@login_required
@role_required(["super_admin", "librarian"])
def book_details_page(request):
    book_details = BookDetails.objects.filter(is_acitve=True).order_by("-updated_at")
    categories = BookCategory.objects.all()
    book_details_list = []

    for book in book_details:
        isbn = book.isbn
        title = book.title.title()
        author = book.author.title()
        publication_year = book.publication_year
        total_copies = book.total_copies
        available_copies = book.available_copies
        category_id = book.category.choice

        # ================================>
        print("ISBN             : ", isbn)
        print("TITLE            : ", title)
        print("AUTHOR           : ", author)
        print("PUBLICATION YEAR : ", publication_year)
        print("TOTAL COPIES     : ", total_copies)
        print("AVAILABLE COPIES : ", available_copies)
        print("CATEGORY         :", category_id)
        # ================================>

        book_details_list.append({
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author,
            "publication_year": book.publication_year,
            "total_copies": book.total_copies,
            "available_copies": book.available_copies,
            "category": book.category.choice,
        })
    return render(request, "book_details/book_details.html", {"book_details" : book_details_list, "categories": categories})

@csrf_exempt
def book_update_request(request):
    print("HELLOW")
    if request.method == "POST":
        data = json.loads(request.body)
        isbn = data.get("isbn")
        title = data.get("title")
        author = data.get("author")
        category = data.get("category")
        publication_year = data.get("publication_year")
        add_copies = data.get("add_copies")
        add_copies = int(add_copies) if add_copies not in [None, ""] else 0
        total_copies = data.get("total_copies")
        available_copies = data.get("available_copies")

        # ================================>
        print("ISBN             :", isbn)
        print("TITLE            :", title)
        print("AUTHOR           :", author)
        print("CATEGORY         :", category)
        print("PUBLICATION YEAR :", publication_year)
        print("ADD COPIES       :", add_copies)
        print("TOTAL COPIES     :", total_copies)
        print("AVAILABLE COPIES :", available_copies)
        # ================================>

        try:
            book = BookDetails.objects.get(isbn=isbn)

            if data.get("title"):
                book.title = data.get("title")

            if data.get("author"):
                book.author = data.get("author")

            if data.get("category"):
                book.category = BookCategory.objects.get(id=category)

            if data.get("publication_year"):
                book.publication_year = data.get("publication_year")

            if add_copies > 0:
                book.total_copies += add_copies
                book.available_copies += add_copies

            book.save()

            return JsonResponse({
                "status": "success",
                "message": "Book updated successfully"
            })

        except BookDetails.DoesNotExist:
            BookDetails.objects.create(
                isbn=isbn,
                title=data.get("title"),
                author=data.get("author"),
                category=data.get("category"),
                publication_year=data.get("publication_year"),
                total_copies=add_copies,
                available_copies=add_copies
            )

            return JsonResponse({
                "status": "success",
                "message": "Data received successfully",
                "received_data": data
            })

    return JsonResponse({
        "status": "error",
        "message": "Something Went Wrong!"
    }, status=405)



@csrf_exempt
def book_delete_request(request):
    if request.method == "POST":
        data = json.loads(request.body)
        isbn = data.get("isbn")
        # ================================>
        print("ISBN     : ",isbn)
        # ================================>
        try:
            book = BookDetails.objects.get(isbn=isbn)
            if book.is_acitve:
                book.is_acitve = False
                book.save()

                return JsonResponse({
                    "status": "success",
                    "message": "Book deleted successfully"
                }, status=200)

            else:
                return JsonResponse({
                    "status": "error",
                    "message": "Book is already inactive"
                }, status=400)

        except BookDetails.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Book not found"
            }, status=404)

        return JsonResponse({
            "status": "error",
            "message": "Book is already inactive or invalid request"
        }, status=400)


    return JsonResponse({
        "status": "error",
        "message": "Error Something Went Wrong"
    }, status=400)


@login_required
@role_required(["super_admin", "librarian"])
def borrow_records(request):
    issuemaintenance = IssueMaintanence.objects.all().order_by('-created_at')

    member_id = request.GET.get('member')
    book_id = request.GET.get('book')
    status = request.GET.get('status')

    if member_id and member_id != "":
        issuemaintenance = issuemaintenance.filter(member_id=member_id)
    if book_id and book_id != "":
        issuemaintenance = issuemaintenance.filter(book_id=book_id)
    if status and status != "":
        issuemaintenance = issuemaintenance.filter(status=status)

    members = Member.objects.all()
    books = BookDetails.objects.all()

    return render(request, "records/records.html", {"issuemaintenance": issuemaintenance, "members": members, "books": books,})


@login_required
@role_required(["super_admin", "librarian"])
def borrow_records_register(request):
    member = Member.objects.values("id", "name").order_by("name")
    books = BookDetails.objects.values("id", "title", "available_copies").order_by("title")
    if request.method == "POST":
        role = request.session.get("role")
        member_id = request.POST.get("member_id")
        book_id = request.POST.get("book_id")
        quantity = int(request.POST.get("quantity") or 0)
        status = request.POST.get("status")
        issue_date = datetime.strptime(request.POST.get("issue_date"),"%Y-%m-%d").date()
        due_date = datetime.strptime(request.POST.get("due_date"),"%Y-%m-%d").date()
        
        if issue_date < date.today():
            messages.error(request, "Issue Date cannot be in the past!")
            return redirect("records_register")

        if role == "super_admin":
            print("=================>  SUPERUSER")
            user_id = request.session.get("superuser_id")
            # ================================>
            print("SuperUser ID: ", user_id)
            print("Member ID:", member_id)
            print("Book ID:", book_id)
            print("Quantity ID:", quantity)
            print("Status:", status)
            print("Issue Date:", issue_date)
            print("Due Date:", due_date)
            # ================================>

            member_obj = Member.objects.get(id=member_id)
            book_obj = BookDetails.objects.get(id=book_id)
            librarian_obj = Librarian.objects.filter(is_active=True).first()

            if due_date > member_obj.membership_date:
                messages.error(request, "Due date cannot exceed the member's membership expiry date!")
                return redirect("records_register")

            if not librarian_obj:
                messages.error(request, "No active librarian found.")
                return redirect("records_register")

            borrowed_data = IssueMaintanence.objects.filter(member=member_obj,status="issued").aggregate(total_books=Sum("books_number"))

            current_borrowed = borrowed_data["total_books"] or 0
            if current_borrowed + quantity > 5:
                remaining = 5 - current_borrowed
                if remaining <= 0:
                    messages.error(request,"You already borrowed the maximum limit of 5 books!")
                else:
                    messages.error(request, f"You can borrow only {remaining} more book(s)")
                return redirect("records_register")

            
            if book_obj.available_copies < quantity:
                messages.error(request, "Not enough books available!")
                return redirect("records_register")

            rows_updated = BookDetails.objects.filter(id=book_id).update(
                available_copies=F('available_copies') - quantity
            )

            if rows_updated == 1:
                IssueMaintanence.objects.create(
                    librarian=librarian_obj,
                    member=member_obj,
                    book=book_obj,
                    status=status,
                    issue_date=issue_date,
                    due_date=due_date,
                    books_number=quantity
                )
                messages.success(request, "Book issued successfully!")
                return redirect("records_register")
            else:
                print("No record updated (book not found)")
                return redirect("records_register")

            messages.success(request, "Borrow record saved successfully!")
            return redirect("records_register")
        else:
            print("=================> LIBRARIAN")
            librarian_id = request.session.get("librarian_id")
            # ================================>
            print("Librarian ID: ", librarian_id)
            print("Member ID:", member_id)
            print("Book ID:", book_id)
            print("Quantity ID:", quantity)
            print("Status:", status)
            print("Issue Date:", issue_date)
            print("Due Date:", due_date)
            # ================================>

            member_obj = Member.objects.get(id=member_id)
            book_obj = BookDetails.objects.get(id=book_id)
            librarian_obj = Librarian.objects.get(id=librarian_id)

            if not librarian_obj:
                messages.error(request, "No active librarian found.")
                return redirect("records_register")

            borrowed_data = IssueMaintanence.objects.filter(member=member_obj,status="issued").aggregate(total_books=Sum("books_number"))

            current_borrowed = borrowed_data["total_books"] or 0
            if current_borrowed + quantity > 5:
                remaining = 5 - current_borrowed
                if remaining <= 0:
                    messages.error(request,"You already borrowed the maximum limit of 5 books!")
                else:
                    messages.error(request, f"You can borrow only {remaining} more book(s)")
                return redirect("records_register")

            
            if quantity > 5:
                messages.error(request, "You cannot issue more than 5 books at a time!")
                return redirect("records_register")
            
            if book_obj.available_copies < quantity:
                messages.error(request, "Not enough books available!")
                return redirect("records_register")

            rows_updated = BookDetails.objects.filter(id=book_id).update(
                available_copies=F('available_copies') - quantity
            )

            if rows_updated == 1:
                IssueMaintanence.objects.create(
                    librarian=librarian_obj,
                    member=member_obj,
                    book=book_obj,
                    status=status,
                    issue_date=issue_date,
                    due_date=due_date,
                    books_number=quantity
                )
                messages.success(request, "Book issued successfully!")
                return redirect("records_register")
            else:
                print("No record updated (book not found)")
                return redirect("records_register")
            messages.success(request, "Borrow record saved successfully!")
            return redirect("records_register")

    return render(request, "records_register/records_register.html", {"member": member, "books": json.dumps(list(books))})



@login_required
@role_required(["super_admin", "librarian"])
def borrow_returns(request):
    total_books = BookDetails.objects.count()
    total_members = Member.objects.count()
    total_fine = FineMaintanence.objects.aggregate(total=Sum("fine_cost"))["total"]
    overdue_books = FineMaintanence.objects.filter(is_return=False).count()
    total_issued_books = (IssueMaintanence.objects.filter(status="issued").aggregate(total=Sum("books_number"))["total"] or 0)

    # ================================>
    print("TOTAL BOOKS          : ", total_books)
    print("TOTAL MEMBERS        : ", total_members)
    print("TOTAL FINE           : ", total_fine)
    print("OVER DUE BOOKS       : ", overdue_books)
    print("CURRENT ISSUED BOOKS : ", total_issued_books)
    # ================================>
    whole_data = {
        'total_books' : total_books,
        'total_members' : total_members,
        'total_fine' : total_fine,
        'overdue_books' : overdue_books,
        'total_issued_books' : total_issued_books
    }
    return render(request, "returns/return.html", whole_data)





def record_report(request):
    top_books = (
        IssueMaintanence.objects.values("book_id","book__isbn","book__title","book__author","book__publication_year","book__total_copies","book__available_copies","book__category__choice",)
        .annotate(
            borrow_count=Count("id"),
            latest_issue=Max("issue_date"),
            latest_return=Max("return_date"),
            latest_due=Max("due_date"),
        )
        .order_by("-borrow_count")[:10]
    )

    result = []
    for book in top_books:
        book_id = book["book_id"]
        top_member_row = (
            IssueMaintanence.objects
            .filter(book_id=book_id)
            .values("member__name")
            .annotate(total=Count("id"))
            .order_by("-total")
            .first()
        )

        latest_issue = (
            IssueMaintanence.objects
            .filter(book_id=book_id)
            .select_related("librarian", "member")
            .order_by("-issue_date")
            .first()
        )

        fine_sum = (
            FineMaintanence.objects
            .filter(book_id=book_id, is_paid=True)
            .aggregate(total=Sum("paid_cost"))
        )["total"] or 0

        result.append({
"book_id": book_id,
            "isbn": book["book__isbn"],
            "title": book["book__title"],
            "author": book["book__author"],
            "category": book["book__category__choice"],
            "publication_year": book["book__publication_year"],
            "total_copies": book["book__total_copies"],
            "available_copies": book["book__available_copies"],
            "borrow_count": book["borrow_count"],

            "top_member": top_member_row["member__name"] if top_member_row else None,

            "librarian": (
                f"{latest_issue.librarian.name} {latest_issue.librarian.surname}"
                if latest_issue else None
            ),

            "latest_issue_date": latest_issue.issue_date.date().isoformat() if latest_issue and latest_issue.issue_date else None,
            "latest_return_date": latest_issue.return_date.date().isoformat() if latest_issue and latest_issue.return_date else None,
            "latest_due_date": latest_issue.due_date.date().isoformat() if latest_issue and latest_issue.due_date else None,

            "total_fine_collected": fine_sum,
        })

    return JsonResponse({
        "status": "success",
        "top_borrowed_books": result
    })






















# =====================================================================================================================================================
# =====================================================================================================================================================
# =====================================================================================================================================================
# =====================================================================================================================================================
                                                                        # REST API #
# =====================================================================================================================================================
# =====================================================================================================================================================
# =====================================================================================================================================================
# =====================================================================================================================================================

@api_view(["GET","POST","PUT","PATCH","DELETE"])
def member_api(request):
    if request.method == "GET":
        member = Member.objects.all()
        serializer = MemberSerializers(member, many=True)
        return Response(serializer.data, status=200)
    elif request.method == "POST":
        serializer = MemberSerializers(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": f"{user.name} registered successfully!"}, status=201)
        else:
            return Response(serializer.errors, status=400)
    elif request.method == "PUT":
        member = Member.objects.get(id=id)
        if member.id is None:
            return Response(
                {"error": "Member not found"},
                status=404
            )
        serializer = MemberSerializers(member,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Member updated successfully"},
                status=200
            )
        return Response(serializer.errors, status=400)
    elif request.method == "PATCH":
        member = Member.objects.get(id=id)
        if member.id is None:
            return Response(
                {"error": "Member not found"},
                status=404
            )
        serializer = MemberSerializers(member,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Member updated partially"},
                status=200
            )
        return Response(serializer.errors, status=400)
    elif request.method == "DELETE":
        member = Member.objects.get(id=id)
        if member.id is None:
            return Response(
                {"error": "Member not found"},
                status=404
            )
        member.delete()
        return Response(
            {"message": "Member deleted successfully"},
            status=200
        )



@api_view(["GET","POST","PUT","PATCH","DELETE"])
def books_api(request):
    if request.method == "GET":
        books = BookDetails.objects.all()
        serializer = BookDetailsSerializers(books, many=True)
        return Response(serializer.data, status=200)
    elif request.method == "POST":
        serializer = BookDetailsSerializers(data = request.data)
        if serializer.is_valid():
            book = serializer.save()
            return Response({"message" : f"{book.title} registered successfully!"})
        else:
            return Response(serializer.errors, status=400)
    elif request.method == "PUT":
        book = BookDetails.objects.get(id=id)
        if book.id is None:
            return Response(
                {"error": "Book not found"},
                status=404
            )
        serializer = BookDetailsSerializers(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Book updated successfully (PUT)"},
                status=200
            )
        return Response(serializer.errors, status=400)
    elif request.method == "PATCH":
        book = BookDetails.objects.get(id=id)
        if book.id is None:
            return Response(
                {"error": "Book not found"},
                status=404
            )
        serializer = BookDetailsSerializers(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Book updated partially (PATCH)"},
                status=200
            )
        return Response(serializer.errors, status=400)
    elif request.method == "DELETE":
        book = BookDetails.objects.get(id=id)
        if book.id is None:
            return Response(
                {"error": "Book not found"},
                status=404
            )
        book.delete()   
        return Response(
            {"message": "Book deleted successfully"},
            status=200
        )     
