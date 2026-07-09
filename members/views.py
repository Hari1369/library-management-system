from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.db import transaction, IntegrityError
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Librarian, Member, BookDetails, BookCategory, IssueMaintanence, FineMaintanence, PasswordResetOTP
from .serializers import LibrarianSerializers, MemberSerializers, BookDetailsSerializers
from .forms import LoginForm, LibrarianFrom, BookCategoryForm, BookForm, MemberFrom, IssueMaintanenceForm
from .decorators import role_required
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime, date
from django.db.models import Sum, Count, Max, Sum
from django.db.models import F
from django.utils import timezone
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
import json
today = timezone.now().date()

def login_page(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            print("USERNAME :", username)
            print("PASSWORD :", password)

            user = authenticate(request, username=username, password=password)
            librarian = Librarian.objects.filter(username=username).first()

            if librarian and librarian.update_requested_at:
                if timezone.now().date() > librarian.update_requested_at.date():
                    librarian.is_active = False
                    librarian.save()

                    if user:
                        user.is_active = False
                        user.save()

                    messages.error(
                        request,
                        "Your account has been temporarily disabled. Please wait for administrator approval."
                    )
                    return render(request, "log_in/log_in.html", {"form": form})

            if user is not None:
                if not user.is_active:
                    messages.error(request, "Account disabled.")
                    return render(request, "log_in/log_in.html", {"form": form})

                login(request, user)

                request.session["id"] = user.id
                request.session["username"] = user.username

                if user.is_superuser and user.is_staff:
                    request.session["superuser_id"] = user.id
                    request.session["role"] = "super_admin"

                elif librarian and librarian.is_active:
                    request.session["librarian_id"] = librarian.id
                    request.session["role"] = "librarian"

                else:
                    messages.error(request, "Unauthorized role.")
                    return render(request, "log_in/log_in.html", {"form": form})

                return redirect("dashboard_page")

            else:
                messages.error(request, "Invalid username or password.")

    return render(request, "log_in/log_in.html", {"form": form})


# def login_page(request):
#     form = LoginForm()
#     if request.method == "POST":
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data["username"]
#             password = form.cleaned_data["password"]
#             # ================================>
#             print("USERNAME : ", username)
#             print("PASSWORD : ", password)
#             # ================================>
#             user = authenticate(request, username=username, password=password)
#             librarian = Librarian.objects.filter(username=username,is_active=True).first()

#             if user is not None:
#                 login(request, user)
#                 request.session["id"] = user.id
#                 request.session["username"] = user.username
#                 if not user.is_active:
#                     messages.error(request, "Account disabled.")
#                     return render(request, "log_in/log_in.html", {"form": form})
#                 if user.is_superuser and user.is_staff:
#                     request.session["superuser_id"] = user.id
#                     request.session["role"] = "super_admin"
#                 elif librarian:
#                     request.session["librarian_id"] = librarian.id
#                     request.session["role"] = "librarian"
#                 else:
#                     messages.error(request, "Unauthorized role.")
#                     return render(request, "log_in/log_in.html", {"form": form})

#                 return redirect("dashboard_page")
#             else:
#                 messages.error(request, "Invalid username or password.")
#     return render(request, "log_in/log_in.html", {"form": form})


def logout_page(request):
    logout(request)
    return redirect('log_in')

@login_required
@role_required(["super_admin","librarian"])
def dashboard_page(request):
    return render(request, "librarians_dashboard/librarians_dashboard.html")

def dashboard_upper(request):
    total_books = BookDetails.objects.count()
    total_members = Member.objects.count()
    total_fine = FineMaintanence.objects.aggregate(total=Sum("fine_cost"))["total"]
    overdue_books = FineMaintanence.objects.filter(is_return=False).count()
    total_issued_books = (IssueMaintanence.objects.filter(status="issued").aggregate(total=Sum("books_number"))["total"] or 0)
    issued_today = IssueMaintanence.objects.filter(status="issued", created_at__date=today).count()

    # ================================>
    print("TOTAL BOOKS          : ", total_books)
    print("TOTAL MEMBERS        : ", total_members)
    print("TOTAL FINE           : ", total_fine)
    print("OVER DUE BOOKS       : ", overdue_books)
    print("CURRENT ISSUED BOOKS : ", total_issued_books)
    print("ISSUED TODAY         : ", issued_today)
    # ================================>

    data = {
        "total_books": total_books,
        "total_members": total_members,
        "total_fine": total_fine,
        "overdue_books": overdue_books,
        "total_issued_books": total_issued_books,
        "issued_today": issued_today
    }
    return JsonResponse(data)


def dashboard_book_data(request):
    print("TRIGGER 1 ")
    book_data_1 = (IssueMaintanence.objects.filter(issue_date__date=today).values("book__title","librarian__name","member__first_name","member__last_name","issue_date","member__is_active","member__created_at",).annotate(total_issued=Count("id")).order_by("-total_issued")[:5])
    book_data_list = []
    for item in book_data_1:
        book_title = item["book__title"]
        librarian_name = item["librarian__name"]
        member_name = f"{item['member__first_name']} {item['member__last_name'] or ''}".strip()
        issue_date = item["issue_date"]
        total_issued = item["total_issued"]
        member_is_active = item["member__is_active"]
        issue_date_formatted = issue_date.strftime("%d-%m-%Y")
        created_at = item["member__created_at"]
        created_at_formatted = created_at.strftime("%d-%m-%Y %H:%M:%S")

        # ================================>
        print("BOOK TITLE       : ", book_title)
        print("LIBRARIAN        : ", librarian_name)
        print("MEMBER NAME      : ", member_name)
        print("MEMBER IS ACTIVE : ", member_is_active)
        print("ISSUED DATE      : ", issue_date_formatted)
        print("TOTAL ISSUED     : ", total_issued)
        print("REGISTERED AT     : ", created_at_formatted)
        # ================================>

        book_data_list.append({
            "book_title": book_title,
            "librarian_name": librarian_name,
            "member_name": member_name,
            "issue_date": issue_date_formatted,
            "total_issued": total_issued,
            "member_is_active": member_is_active,
            "registered_at": created_at_formatted,
        })

    return JsonResponse({
        "status": "success",
        "book_data_list": book_data_list
    })

def dashboard_lowest_books(request):
    print("TRIGGER 2 ")
    all_books = BookDetails.objects.all()
    book_less_list = []
    low_stock_books = []
    for book in all_books:
        if book.available_copies < 5:
            low_stock_books.append(book)

    issues = IssueMaintanence.objects.filter(book__in=low_stock_books)
    data = issues.values("book__title","book__author","book__category__choice","book__total_copies","book__available_copies","member__name","member__is_active",)

    for item in data:
        book_title = item['book__title']
        book_author = item['book__author']
        category_choice = item['book__category__choice']
        total_copies = item['book__total_copies']
        available_copies = item['book__available_copies']
        member_name = item['member__name']
        member_isactive = item['member__is_active']

        # ================================>
        print("BOOK_TITLE       : ", book_title)
        print("BOOK AUTHOR      : ", book_author)
        print("CATEGORY CHOICE  : ", category_choice)
        print("TOTAL COPIES     : ", total_copies)
        print("AVAILABLE COPIES : ", available_copies)
        print("MEMBER NAME      : ", member_name)
        print("MEMBER ISACTIVE  : ", member_isactive)
        # ================================>

        book_less_list.append({
            "book_title": book_title,
            "book_author": book_author,
            "category_choice": category_choice,
            "total_copies": total_copies,
            "available_copies": available_copies,
            "member_name": member_name,
            "member_isactive": member_isactive,
        })

    return JsonResponse({"status": "ok", "book_less_list" : book_less_list})

def dashboard_total_activemember(request):
    print("TRIGGER 3")
    total_active_memebrs = Member.objects.filter(is_active=True, is_expired=False)
    activemembers = []
    for member in total_active_members:
        registered_at =  member.created_at.strftime("%d-%m-%Y %H:%M:%S")
        name = member.name
        email = member.email
        membership_date = member.membership_date.strftime("%d-%m-%Y")
        is_active = member.is_active
        is_expired = member.is_expired

        # ================================>
        print("REGISTERED AT    : ", registered_at)
        print("NAME             : ", name)
        print("EMAIL            : ", email)
        print("MEMBERSHIP DATE  : ", membership_date)
        print("IS_ACTIVE        : ", is_active)
        print("IS_EXPIRED       : ", is_expired)
        # ================================>
        
        activemembers.append({
            "registered_at": registered_at,
            "name": name,
            "email": email,
            "membership_date": membership_date,
            "is_active": is_active,
            "is_expired": is_expired,
        })

    return JsonResponse({"status": "ok", "activemembers" : activemembers})


def dashboard_total_inactivemember(request):
    print("TRIGGER 3")
    total_inactive_memebrs = Member.objects.filter(is_active=False, is_expired=True)
    is_activemembers = []
    for member in total_inactive_memebrs:
        registered_at = member.created_at.strftime("%d-%m-%Y %H:%M:%S")
        name = member.name
        email = member.email
        membership_date =member.membership_date.strftime("%d-%m-%Y")
        is_active = member.is_active
        is_expired = member.is_expired

        # ================================>
        print("REGISTERED AT    : ", registered_at)
        print("NAME             : ", name)
        print("EMAIL            : ", email)
        print("MEMBERSHIP DATE  : ", membership_date)
        print("IS_ACTIVE        : ", is_active)
        print("IS_EXPIRED       : ", is_expired)
        # ================================>
        
        is_activemembers.append({
            "registered_at": registered_at,
            "name": name,
            "email": email,
            "membership_date": membership_date,
            "is_active": is_active,
            "is_expired": is_expired,
        })

    return JsonResponse({"status": "ok", "is_activemembers" : is_activemembers})





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
                return render(request,"librarians_registration/librarians_registration.html",{"form": form,"error": "Username already exists!"})
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
                        password=make_password(password),
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

        # # ================================>
        # print("ID               : ", id)
        # print("USERNAME         : ", username)
        # print("PASSWORD         : ", password)
        # print("NAME             : ", name)
        # print("SURNAME          : ", surname)
        # print("EMAIL            : ", email)
        # print("PHONE NUMBER     : ", phone_number)
        # print("ADDRESS          : ", address)
        # print("IS ACTIVE        : ", is_active)
        # # ================================>

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
            "created_at": user.created_at.strftime("%d-%m-%Y %H:%M:%S"),
        })
    return render(request, "librarians_details/librarians_details.html", {"users" : user_list})



@csrf_exempt
def librarian_update_request(request, user_id):
    if request.method != "PUT":
        return JsonResponse({"status": "error","message": "Invalid Request"},status=405)

    try:
        # data = json.loads(request.body)
        # librarian_id = request.session.get("user_id")
        # librarian = Librarian.objects.filter(id=librarian_id).first()

        data = json.loads(request.body)
        librarian = Librarian.objects.filter(id=user_id).first()


        if librarian is None:
            return JsonResponse({"status": "error","message": "Librarian not found."},status=404)

        name = data.get("name").title()
        surname = data.get("surname").title()
        email = data.get("email")
        phone = data.get("phone")
        address = data.get("address").title()
        # user = User.objects.filter(username=username).first()

        if (
            librarian.name == name and
            librarian.surname == surname and
            librarian.email == email and
            librarian.phone_number == phone and
            librarian.address == address
        ):
            return JsonResponse({"status": "error", "message": "No Change Found"},status=400)

        librarian.name = name
        librarian.surname = surname
        librarian.email = email
        librarian.phone_number = phone
        librarian.address = address
        librarian.update_requested_at = timezone.now()
        librarian.save()

        return JsonResponse({"status": "success","message": "Profile updated successfully. Your account will remain active today. From tomorrow, administrator approval will be required."})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
def librarian_delete_request(request, user_id):
    if request.method == "DELETE":
        data = json.loads(request.body)
        username = data.get("username")
        name = data.get("name").title()
        email = data.get("email")
        is_active = str(data.get("is_active")).lower() == "true"

        # ================================>
        print("USER ID      : ", user_id)
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
        
        librarian = Librarian.objects.filter(id=user_id).first()
        if librarian is None:
            return JsonResponse({"status": "error", "message": "Librarian not found."}, status=404) 
                
        try:
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
            first_name = form.cleaned_data["first_name"].title()
            last_name = form.cleaned_data["last_name"].title()
            email = form.cleaned_data["email"]
            phone_number = form.cleaned_data["phone_number"]
            address = form.cleaned_data["address"].title()
            membership_date = form.cleaned_data["membership_date"]
            is_active = form.cleaned_data["is_active"]

            if not membership_date:
                print("membership_date is empty or null")
                messages.error(request, "membership_date is empty or null")
                return redirect("member_registration")

            if membership_date < date.today():
                messages.error(request, "Membership date cannot be in the past.")
                return redirect("member_registration")

            # ================================>
            print("FIRST NAME                 : ",  first_name)
            print("LAST NAME                 : ",  last_name)
            print("EMAIL                : ",  email)
            print("PHONE NUMBER         : ",  phone_number)
            print("ADDRESS              : ",  address)
            print("MEMBERSHIP DATE      : ",  membership_date)
            print("ACTIVE               : ",  is_active)
            # ================================>

            if Member.objects.filter(first_name=first_name).exists():
                messages.error(request, "Member already exists.")
                return redirect("member_registration")
            
            try:
                with transaction.atomic():
                    member_insert = Member.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        phone_number=phone_number,
                        address=address,
                        membership_date=membership_date,
                        is_active=is_active,
                    )                 
                messages.success(request, f"Member {first_name} {last_name} inserted successfully!")
                return redirect("member_registration")

            except IntegrityError:
                messages.error(request, "Database error occurred. Try again.")
                return redirect("member_registration")
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
        first_name = i.first_name.title()
        last_name = (i.last_name or "").title()
        email = i.email
        phone_number = i.phone_number
        address = i.address.title()
        membership_date = i.membership_date.strftime("%d-%m-%Y") if i.membership_date else ""
        is_active = i.is_active
        is_expired = i.is_expired
        created_at = i.created_at

        # ================================>
        print("ID               : ", id)
        print("FIRST NAME       : ", first_name)
        print("LAST NAME        : ", last_name)
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
            "first_name" : first_name,
            "last_name" : last_name,
            "address" : address,
            "email" : email,
            "phone_number" : phone_number,
            "membership_date": membership_date,
            "is_active" : is_active,
            "is_expired" : is_expired,
            "created_at" : created_at.strftime("%d-%m-%Y %H:%M:%S"),
        })
    return render(request, "member_details/member_details.html", {"members": member_list})

@csrf_exempt
def member_update_request(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        member_id = data.get("id")
        first_name = data.get("first_name").title()
        last_name = data.get("last_name").title()
        email = data.get("email")
        phone = data.get("phone")
        address = data.get("address")
        membership_date = data.get("membership_date")
        if membership_date:
            membership_date = datetime.strptime(membership_date, "%Y-%m-%d").date()

        if not member_id:
            return JsonResponse({
                "status": "error",
                "message": "Member ID is required"
            }, status=400)   


        if membership_date < date.today():
            return render(request, "member_registration/member_registration.html", {"form": form, "error": "Membership date cannot be in the past."})  
        # ================================>
        print("ID                   :", member_id)
        print("FIRST NAME                 :", first_name)
        print("LAST NAME                 :", last_name)
        print("EMAIL                :", email)
        print("PHONE                :", phone)
        print("ADDRESSS             :", address)
        print("MEMBERSHIP DATE      :", membership_date)
        # ================================>

        try:
            member = Member.objects.get(id=member_id)
            if (member.first_name == first_name and member.last_name == last_name and member.email == email and member.phone_number == phone and member.address == address and member.membership_date == membership_date):
                return JsonResponse({"status": "error","message": "No changes detected. Data already up to date."})

            member.first_name = first_name
            member.last_name = last_name
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
                return JsonResponse({
                    "status": "error",
                    "message": "Book is already exists"
                }, status=404)

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
                    messages.success(request, f"Book {book_insert.isbn} with Author {book_insert.author} Added Successfully!")
                    return redirect("book_registration")
            except IntegrityError:
                return render(request, "book_registration/add_books.html", {"form": form,"error": "Database error occurred. Try again."})
    return render(request, "book_registration/add_books.html", {"form": form})

@login_required
@role_required(["super_admin", "librarian"])
def book_details_page(request):
    book_details = BookDetails.objects.filter(is_active=True).order_by("-updated_at")
    categories = BookCategory.objects.all()
    book_details_list = []

    for book in book_details:
        book_id = book.id
        isbn = book.isbn
        title = book.title.title()
        author = book.author.title()
        publication_year = book.publication_year
        total_copies = book.total_copies
        available_copies = book.available_copies
        category_id = book.category.choice

        # # ================================>
        # print("ISBN             : ", isbn)
        # print("TITLE            : ", title)
        # print("AUTHOR           : ", author)
        # print("PUBLICATION YEAR : ", publication_year)
        # print("TOTAL COPIES     : ", total_copies)
        # print("AVAILABLE COPIES : ", available_copies)
        # print("CATEGORY         :", category_id)
        # # ================================>

        book_details_list.append({
            "book_id": book_id,
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
def book_update_request(request, book_id):
    print("HELLOW")
    if request.method == "PUT":
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
            book = BookDetails.objects.filter(id=book_id).first()
            if (title == book.title and author == book.author and str(publication_year) == str(book.publication_year) and add_copies == 0 and (category is None or int(category) == (book.category.id if book.category else None))):
                return JsonResponse({
                    "status": "error",
                    "message": "No changes detected. Please update something before saving."
                })

            copies_added_flag = False
            added_copies_value = 0


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
                
                copies_added_flag = True
                added_copies_value = add_copies


            book.save()
            message = "Book updated successfully"

            if copies_added_flag:
                message = (f"{added_copies_value} copies added successfully. " f"now total copies are {book.total_copies}.")

            return JsonResponse({
                "status": "success",
                "message": message
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

            message = "Book created successfully"
            if add_copies > 0:
                message = (f"{add_copies} copies added successfully. " f"total copies are {book.total_copies}.")


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
def book_delete_request(request, book_id):
    if request.method == "DELETE":
        data = json.loads(request.body)
        isbn = data.get("isbn")
        # ================================>
        print("ISBN     : ",isbn)
        print("BOOK ID  : ",book_id)
        # ================================>
        try:
            book = BookDetails.objects.get(id=book_id)
            if book.is_active:
                book.is_active = False
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
    member = Member.objects.values("id", "first_name", "last_name").order_by("first_name")
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
    top_books = (IssueMaintanence.objects.values(
            "book_id",
            "book__isbn",
            "book__title",
            "book__author",
            "book__publication_year",
            "book__total_copies",
            "book__available_copies",
            "book__category__choice",
        ).annotate(
            borrow_count=Count("id"),
            latest_issue=Max("issue_date"),
            latest_return=Max("return_date"),
            latest_due=Max("due_date"),
        ).order_by("-borrow_count")[:10])
    result = []
    for book in top_books:
        book_id = book["book_id"]

        top_member_row = (IssueMaintanence.objects.filter(book_id=book_id).values("member__first_name").annotate(total=Count("id")).order_by("-total").first())
        if top_member_row:
            top_member = top_member_row["member__first_name"]
        else:
            top_member = None
        latest_issue = (IssueMaintanence.objects.filter(book_id=book_id).select_related("librarian", "member").order_by("-issue_date").first())
        fine_sum = (FineMaintanence.objects.filter(book_id=book_id, is_paid=True).aggregate(total=Sum("paid_cost")))["total"] or 0

        if latest_issue and latest_issue.librarian:
            librarian = f"{latest_issue.librarian.name} {latest_issue.librarian.surname}"
        else:
            librarian = None

        if latest_issue:
            latest_issue_date = latest_issue.issue_date.date().isoformat() if latest_issue.issue_date else None
            latest_return_date = latest_issue.return_date.date().isoformat() if latest_issue.return_date else None
            latest_due_date = latest_issue.due_date.date().isoformat() if latest_issue.due_date else None
        else:
            latest_issue_date = None
            latest_return_date = None
            latest_due_date = None

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
            "top_member": top_member,
            "librarian": librarian,
            "latest_issue_date": latest_issue_date,
            "latest_return_date": latest_return_date,
            "latest_due_date": latest_due_date,
            "total_fine_collected": fine_sum,
        })

    return JsonResponse({
        "status": "success",
        "top_borrowed_books": result
    })



# @login_required
# @role_required(["super_admin", "librarian"])
# def return_fineregister(request):
#     if request.method == "POST":
#         librarian = request.POST.get("librarian")
#         member = request.POST.get("member")
#         book = request.POST.get("book")
#         fine_cost = request.POST.get("fine_cost")
#         paid_cost = request.POST.get("paid_cost")

#         is_paid = "is_paid" in request.POST
#         is_returned = "is_returned" in request.POST

#         print(librarian)
#         print(member)
#         print(book)
#         print(fine_cost)
#         print(paid_cost)
#         print(is_paid)
#         print(is_returned)

#         # Here you can save data into database
#         # FineMaintanence.objects.create(
#         #     librarian=librarian,
#         #     member=member,
#         #     book=book,
#         #     fine_cost=fine_cost,
#         #     paid_cost=paid_cost,
#         #     is_paid=is_paid,
#         #     is_returned=is_returned
#         # )

#     return render(
#         request,
#         "return_fineregister/return_fineregister.html"
#     )



# def get_member_issue_details(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Method not allowed"}, status=405)
#     try:
#         data = json.loads(request.body)
#         member_id = data.get("member_id")
#     except (json.JSONDecodeError, AttributeError):
#         return JsonResponse({"error": "Invalid JSON body"}, status=400)

#     if not member_id:
#         return JsonResponse({"error": "No member_id provided"}, status=400)

#     fine_record = (FineMaintanence.objects.filter(member_id=member_id, is_paid=False).select_related("librarian", "book").order_by("-created_at").first()
# )

#     if fine_record:
#         today        = date.today()
#         overdue_date = fine_record.overdue_date
#         overdue_days = max((today - overdue_date).days, 0) if overdue_date else 0
#         issue = (IssueMaintanence.objects.filter(member_id=member_id, book_id=fine_record.book_id, status="issued").order_by("-issue_date").first())
#         if issue:
#             issue_id = issue.id
#         else:
#             issue_id = None
#         return JsonResponse({
#             "issue_id":       issue.id,
#             "fine_record_id": fine_record.id,
#             "librarian_id":   fine_record.librarian.id,
#             "librarian_name": f"{fine_record.librarian.name} {fine_record.librarian.surname}",
#             "book_id":        fine_record.book.id,
#             "book_title":     fine_record.book.title,
#             "fine_cost":      fine_record.fine_cost,
#             "overdue_days":   overdue_days,
#         })

#     try:
#         issue = (IssueMaintanence.objects.filter(member_id=member_id, status="issued").select_related("librarian", "book").latest("issue_date"))
#     except IssueMaintanence.DoesNotExist:
#         return JsonResponse({"error": "This member has not been issued any books."})
#     today        = date.today()
#     due_date     = issue.due_date.date() if issue.due_date else None
#     overdue_days = max((today - due_date).days, 0) if due_date else 0
#     fine_cost    = overdue_days * 10

#     return JsonResponse({
#         "issue_id":       issue.id,
#         "fine_record_id": None,
#         "librarian_id":   issue.librarian.id,
#         "librarian_name": f"{issue.librarian.name} {issue.librarian.surname}",
#         "book_id":        issue.book.id,
#         "book_title":     issue.book.title,
#         "fine_cost":      fine_cost,
#         "overdue_days":   overdue_days,
#     })


# @login_required
# @role_required(["super_admin", "librarian"])
# def return_fineregister(request):
#     members = Member.objects.filter(is_active=True)
#     if request.method == "POST":
#         member_id = request.POST.get("member")
#         issue_id = request.POST.get("issue_id")
#         fine_record_id = request.POST.get("fine_record_id")
#         librarian_id = request.POST.get("librarian")
#         book_id = request.POST.get("book")
#         fine_cost = int(request.POST.get("fine_cost") or 0)
#         paid_cost = int(request.POST.get("paid_cost") or 0)
#         is_paid = "is_paid"     in request.POST
#         is_return = "is_returned" in request.POST

#         # ========================================>
#         print("MEMBER ID    : ", member_id)
#         print("ISSUE ID     : ", issue_id)
#         print("RECORD ID    : ", fine_record_id)
#         print("LIBRARIAN ID : ", librarian_id)
#         print("BOOK ID      : ", book_id)
#         print("FINE CAST    : ", fine_cost)
#         print("PAID_CAST    : ", paid_cost)
#         print("IS_PAID      : ", is_paid)
#         print("IS_RETURN    : ", is_return)
#         # ========================================>


#         try:
#             remain_cost = fine_cost - paid_cost
#         except ValueError:
#             return render(request, "return_fineregister/return_fineregister.html", {"members": members,"error": "Invalid fine or paid cost value!",})

#         if paid_cost > fine_cost:
#             return render(request, "return_fineregister/return_fineregister.html", {"members": members,"error": "Paid cost cannot exceed the fine cost!"})


#         if fine_cost > 0 and paid_cost == fine_cost:
#             print("Found")
#             is_paid = True
#         else:
#             is_paid = False

#         if is_paid:
#             paid_time = now()
#         else:
#             paid_time = None


#         try:
#             if fine_record_id:
#                 finemaintanence_data = FineMaintanence.objects.get(id=fine_record_id)
#                 total_paid   = (finemaintanence_data.paid_cost or 0) + paid_cost
#                 remain_cost  = fine_cost - total_paid

#                 if total_paid > fine_cost:
#                     return render(request, "return_fineregister/return_fineregister.html", {
#                         "members": members,
#                         "error": f"Total paid (₹{total_paid}) cannot exceed the fine cost (₹{fine_cost})!",
#                     })

#                 is_paid   = (remain_cost == 0)
#                 paid_time = now() if is_paid else None

#                 finemaintanence_data.paid_cost   = total_paid
#                 finemaintanence_data.remain_cost = remain_cost
#                 finemaintanence_data.is_paid     = is_paid
#                 finemaintanence_data.is_return   = is_return
#                 finemaintanence_data.paid_time   = paid_time
#                 finemaintanence_data.save()
#             else:
#                 if fine_cost == paid_cost:
#                     paid_time =  date.today()
#                 else:
#                     paid_time = None

#                 FineMaintanence.objects.create(
#                     librarian_id = librarian_id,
#                     member_id = member_id,
#                     book_id = book_id,
#                     fine_cost = fine_cost,
#                     paid_cost = paid_cost,
#                     remain_cost = remain_cost,
#                     is_paid = is_paid,
#                     is_return = is_return,
#                     overdue_date = overdue_date,
#                     paid_time = paid_time,
#                 )

#             if issue_id and is_return:
#                 IssueMaintanence.objects.filter(id=issue_id).update(status = "returned", return_date = date.today(),)
#                 messages.success(request, f"Successfully received ₹{paid_cost} from the member.")
#             return redirect("return_fineregister")

#         except Exception as e:
#             print("Something went wrong")
#             return render(request, "return_fineregister/return_fineregister.html", {
#                 "members": members,
#                 "error":   "Something went wrong while saving. Please try again.",
#             })

#     return render(request, "return_fineregister/return_fineregister.html", {"members": members,})






def get_member_issue_details(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        member_id = data.get("member_id")
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    if not member_id:
        return JsonResponse({"error": "No member_id provided"}, status=400)

    fine_record = (
        FineMaintanence.objects.filter(member_id=member_id, is_paid=False)
        .select_related("librarian", "book")
        .order_by("-created_at")
        .first()
    )

    if fine_record:
        today        = date.today()
        overdue_date = fine_record.overdue_date
        overdue_days = max((today - overdue_date).days, 0) if overdue_date else 0

        issue = (
            IssueMaintanence.objects.filter(
                member_id=member_id, book_id=fine_record.book_id, status="issued"
            ).order_by("-issue_date").first()
        )
        issue_id = issue.id if issue else None

        already_paid = fine_record.paid_cost or 0
        # remain_cost should already be stored, but fall back to a calculation just in case
        remain_cost  = fine_record.remain_cost
        if remain_cost is None:
            remain_cost = fine_record.fine_cost - already_paid

        return JsonResponse({
            "issue_id":       issue_id,
            "fine_record_id": fine_record.id,
            "librarian_id":   fine_record.librarian.id,
            "librarian_name": f"{fine_record.librarian.name} {fine_record.librarian.surname}",
            "book_id":        fine_record.book.id,
            "book_title":     fine_record.book.title,
            "fine_cost":      fine_record.fine_cost,
            "already_paid":   already_paid,
            "remain_cost":    remain_cost,
            "overdue_days":   overdue_days,
        })

    try:
        issue = (
            IssueMaintanence.objects.filter(member_id=member_id, status="issued")
            .select_related("librarian", "book")
            .latest("issue_date")
        )
    except IssueMaintanence.DoesNotExist:
        return JsonResponse({"error": "This member has not been issued any books."})

    today        = date.today()
    due_date     = issue.due_date.date() if issue.due_date else None
    overdue_days = max((today - due_date).days, 0) if due_date else 0
    fine_cost    = overdue_days * 10

    return JsonResponse({
        "issue_id":       issue.id,
        "fine_record_id": None,
        "librarian_id":   issue.librarian.id,
        "librarian_name": f"{issue.librarian.name} {issue.librarian.surname}",
        "book_id":        issue.book.id,
        "book_title":     issue.book.title,
        "fine_cost":      fine_cost,
        "already_paid":   0,
        "remain_cost":    fine_cost,
        "overdue_days":   overdue_days,
    })


@login_required
@role_required(["super_admin", "librarian"])
def return_fineregister(request):
    members = Member.objects.filter(is_active=True)
    if request.method == "POST":
        member_id      = request.POST.get("member")
        issue_id       = request.POST.get("issue_id")
        fine_record_id = request.POST.get("fine_record_id")
        librarian_id   = request.POST.get("librarian")
        book_id        = request.POST.get("book")
        fine_cost      = int(request.POST.get("fine_cost") or 0)
        paid_cost      = int(request.POST.get("paid_cost") or 0)
        is_return      = "is_returned" in request.POST

        # ========================================>
        print("MEMBER ID    : ", member_id)
        print("ISSUE ID     : ", issue_id)
        print("RECORD ID    : ", fine_record_id)
        print("LIBRARIAN ID : ", librarian_id)
        print("BOOK ID      : ", book_id)
        print("FINE CAST    : ", fine_cost)
        print("PAID_CAST    : ", paid_cost)
        print("IS_RETURN    : ", is_return)
        # ========================================>

        if paid_cost < 0:
            return render(request, "return_fineregister/return_fineregister.html", {
                "members": members,
                "error": "Paid cost cannot be negative!",
            })

        if paid_cost > fine_cost:
            return render(request, "return_fineregister/return_fineregister.html", {
                "members": members,
                "error": "Paid cost cannot exceed the fine cost!",
            })

        try:
            if fine_record_id:
                finemaintanence_data = FineMaintanence.objects.get(id=fine_record_id)

                # total amount paid across all sessions (previous + this one)
                total_paid  = (finemaintanence_data.paid_cost or 0) + paid_cost
                remain_cost = fine_cost - total_paid

                if total_paid > fine_cost:
                    return render(request, "return_fineregister/return_fineregister.html", {
                        "members": members,
                        "error": f"Total paid (₹{total_paid}) cannot exceed the fine cost (₹{fine_cost})!",
                    })

                is_paid   = (remain_cost == 0)
                paid_time = now() if is_paid else finemaintanence_data.paid_time

                finemaintanence_data.fine_cost   = fine_cost
                finemaintanence_data.paid_cost   = total_paid
                finemaintanence_data.remain_cost = remain_cost
                finemaintanence_data.is_paid     = is_paid
                finemaintanence_data.is_return   = is_return
                finemaintanence_data.paid_time   = paid_time
                finemaintanence_data.save()

            else:
                # brand-new fine record — nothing paid previously
                remain_cost = fine_cost - paid_cost
                is_paid     = (fine_cost > 0 and remain_cost == 0)
                paid_time   = now() if is_paid else None

                FineMaintanence.objects.create(
                    librarian_id  = librarian_id,
                    member_id     = member_id,
                    book_id       = book_id,
                    fine_cost     = fine_cost,
                    paid_cost     = paid_cost,
                    remain_cost   = remain_cost,
                    is_paid       = is_paid,
                    is_return     = is_return,
                    overdue_date  = date.today(),
                    paid_time     = paid_time,
                )

            if issue_id and is_return:
                IssueMaintanence.objects.filter(id=issue_id).update(
                    status="returned", return_date=date.today(),
                )

            if paid_cost > 0:
                messages.success(request, f"Successfully received ₹{paid_cost} from the member.")
            else:
                messages.success(request, "Record updated successfully.")

            return redirect("return_fineregister")

        except Exception as e:
            print("Something went wrong:", e)
            return render(request, "return_fineregister/return_fineregister.html", {
                "members": members,
                "error":   "Something went wrong while saving. Please try again.",
            })
    return render(request, "return_fineregister/return_fineregister.html", {"members": members})



def csv_report(request):
    return render(request, "csv_reports/csv_reports.html")


# def get_member_issue_details(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         member_id = data.get("member_id")
#         if not member_id:
#             return JsonResponse({"error": "No member id provided"}, status=400)
#         try:
#             issue = IssueMaintanence.objects.filter(member_id=member_id,status="issued").select_related("librarian", "book").latest("issue_date")
#             print("ISSUE : ", issue)
#         except IssueMaintanence.DoesNotExist:
#             return JsonResponse({"error": "No active issue found for this member"}, status=404)

#         today = date.today()
#         due_date = issue.due_date.date() if issue.due_date else None
#         if due_date:
#             overdue_days = max((today - due_date).days, 0)
#         else:
#             overdue_days = 0
#         fine_cost = overdue_days * 10

#         return JsonResponse({
#             "librarian_id":   issue.librarian.id,
#             "librarian_name": f"{issue.librarian.name} {issue.librarian.surname}",
#             "book_id":        issue.book.id,
#             "book_title":     issue.book.title,
#             "fine_cost":      fine_cost,
#             "overdue_days":   overdue_days,
#             "issue_id":       issue.id,
#         })




# @login_required
# @role_required(["super_admin", "librarian"])
# def return_fineregister(request):
#     members = Member.objects.filter(is_active=True)

#     # if request.method == "POST":
#     #     member_id  = request.POST.get("member")
#     #     issue_id   = request.POST.get("issue_id")
#     #     librarian_id = request.POST.get("librarian")
#     #     book_id    = request.POST.get("book")
#     #     fine_cost  = request.POST.get("fine_cost")
#     #     paid_cost  = request.POST.get("paid_cost")
#     #     is_paid    = "is_paid"     in request.POST
#     #     is_return  = "is_returned" in request.POST

#     #     try:
#     #         FineMaintanence.objects.create(
#     #             librarian_id = librarian_id,
#     #             member_id    = member_id,
#     #             book_id      = book_id,
#     #             fine_cost    = fine_cost,
#     #             paid_cost    = paid_cost or 0,
#     #             is_paid      = is_paid,
#     #             is_return    = is_return,
#     #         )
#     #         # Mark the issue as returned
#     #         if issue_id and is_return:
#     #             IssueMaintanence.objects.filter(id=issue_id).update(
#     #                 status="returned",
#     #                 return_date=date.today()
#     #             )
#     #         return redirect("return_fineregister")   # adjust to your URL name
#     #     except Exception as e:
#     #         print("Error saving fine record:", e)

#     return render(request, "return_fineregister/return_fineregister.html", {
#         "members": members,
#     })




def password_reset(request):
    return render(request, "forgot_password/forgot_password.html")


@require_POST
def generate_otp(request):
    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip().lower()

        # ========================================>
        print("1")
        print("EMAIL : ", email)
        # ========================================>

        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({"error": "No account found with this email"}, status=404)

        otp = PasswordResetOTP.generate_otp()
        print("OTP : ", otp)
        PasswordResetOTP.objects.filter(user=user).delete()
        PasswordResetOTP.objects.create(user=user, otp=otp)

        send_mail(
            subject="Your Password Reset OTP",
            message=f"Your OTP for password reset is: {otp}\nThis OTP is valid for 10 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return JsonResponse({"message": "OTP sent successfully"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
def verify_otp(request):
    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip().lower()
        otp = data.get("otp", "").strip()

        # ======================================>
        print("2")
        print("EMAIL : ", email)
        print("OTP : ", otp)
        # ======================================>


        if not email or not otp:
            return JsonResponse({"error": "Email and OTP are required"}, status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({"error": "Invalid request"}, status=404)

        otp_data = PasswordResetOTP.objects.filter(user=user, otp=otp).first()

        if not otp_data:
            return JsonResponse({"error": "Invalid OTP"}, status=400)

        if otp_data.is_expired():
            otp_data.delete()
            return JsonResponse({"error": "OTP expired. Please request a new one."}, status=400)

        otp_data.is_verified = True
        otp_data.save()

        return JsonResponse({"message": "OTP verified successfully"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
def reset_password(request):
    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip().lower()
        new_password = data.get("new_password", "")

        if not email or not new_password:
            return JsonResponse({"error": "Email and new password are required"}, status=400)
        if len(new_password) < 4:
            return JsonResponse({"error": "Password must be at least 8 characters"}, status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({"error": "Invalid request"}, status=404)

        otp_data = PasswordResetOTP.objects.filter(user=user, is_verified=True).first()

        if not otp_data:
            return JsonResponse({"error": "OTP verification required before resetting password!"}, status=403)

        if otp_data.is_expired():
            otp_data.delete()
            return JsonResponse({"error": "Session expired. Please restart the process!"}, status=400)

        user.set_password(new_password)
        user.save()

        librarian = Librarian.objects.filter(email=email).first()
        if librarian:
            librarian.password = new_password
            librarian.save()

        PasswordResetOTP.objects.filter(user=user).delete()
        return JsonResponse({"message": "Password reset successful"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




def finereport(request):
    fine_report = FineMaintanence.objects.all().order_by("is_paid")
    return render(request, "fine_report/fine_report.html", {
        "fine_report": fine_report,
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

