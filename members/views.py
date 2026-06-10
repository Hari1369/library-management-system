from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import transaction, IntegrityError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Librarian, Member, BookDetails, BookCategory
from .serializers import LibrarianSerializers, MemberSerializers
from .forms import LoginForm, LibrarianFrom, BookCategoryForm, BookForm
from django.contrib.auth.models import User
from django.contrib import messages
import json



def log_in_page(request):
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
    return render(request, "log_in/log_in.html", {"form": form})


def librarian_registration_page(request):
    form = LibrarianFrom()
    if request.method == "POST":
        form = LibrarianFrom(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            name = form.cleaned_data["name"]
            surname = form.cleaned_data["surname"]
            email = form.cleaned_data["email"]
            phone_number = form.cleaned_data["phone_number"]
            address = form.cleaned_data["address"]
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
                        is_active=is_active
                    )
                    return render(request, "librarians_registration/librarians_registration.html", {"form": form, "success": "Librarian inserted successfully!"})

            except IntegrityError:
                return render(request, "librarians_registration/librarians_registration.html", {"form": form,"error": "Database error occurred. Try again."})

    return render(request, "librarians_registration/librarians_registration.html", {"form": form})


def librarian_details_page(request):
    librarian = Librarian.objects.all()
    user_list = []
    for user in librarian:
        id = user.id
        username = user.username
        password = user.password
        name = user.name
        surname = user.surname
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

    return render(request, "librarians_details/librarians_details.html", {"users": user_list})



def member_registration_page(request):
    # form = MemberFrom()
    # if request.method == "POST":
    #     form = MemberFrom(request.POST)
    #     if form.is_valid():
    #         name = form.cleaned_data["name"]
    #         email = form.cleaned_data["email"]
    #         phone_number = form.cleaned_data["phone_number"]
    #         address = form.cleaned_data["address"]
    #         membership_date = form.cleaned_data["membership_date"]
    #         is_active = form.cleaned_data["name"]
    #         name = form.cleaned_data["name"]
    #         name = form.cleaned_data["name"]

    return render(request, "member_registration/member_registration.html")

def member_details_page(request):
    return render(request, "member_details/member_details.html")



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
            return render(request, "book_category_registration/book_category_registration.html", {"form": form, "category_list": category_list, "success": "Category Added Successfully!"})
        else:
            print(form.errors)

    else:
        return render(request, "book_category_registration/book_category_registration.html", {"form": form, "category_list": category_list})


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



def book_details_page(request):
    return render(request, "book_details/book_details.html")


























# =====================================================================================================================================================
# =====================================================================================================================================================
# =====================================================================================================================================================
# =====================================================================================================================================================
                                                                        # REST API #
# =====================================================================================================================================================
# =====================================================================================================================================================
# =====================================================================================================================================================
# =====================================================================================================================================================

@api_view(["GET","POST"])
def member_api(request):
    if request.method == "GET":
        member = Member.objects.all()
        serializer = MemberSerializers(member, many=True)
        return Response(serializer.data, status=200)
    elif request.method == "POST":
        serializer = MemberSerializers(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message" : f"{user.username} registered successfully!"}, status=201)
        else:
            return Response(serializer.error, status=400)


@api_view(["GET","POST"])
def books_api(request):
    if request.method == "GET":
        books = BookDetails.objects.all()
        serializer = BookDetails(books, many=True)
        return Response(serializer.data, status=200)
    elif request.method == "POST":
        serializer = BookDetailsSerializers(data = request.data)
        if serializer.is_valid():
            book = serializer.save()
            return Response({"message" : f"{book.title} registered successfully!"})