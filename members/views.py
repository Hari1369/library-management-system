from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import transaction, IntegrityError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Users, Member, BookDetails, BookCategory
from .serializers import UserSerializers, MemberSerializers
from .forms import LoginForm, UserFrom
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
    form = UserFrom()
    if request.method == "POST":
        form = UserFrom(request.POST)
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
                if Users.objects.filter(username=username).exists():
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

                    Users.objects.create(
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
    return render(request, "librarians_details/librarians_details.html")

def book_category_registration_page(request):
    return render(request, "book_category_registration/book_category_registration.html")

def book_registration_page(request):
    return render(request, "book_registration/add_books.html")

def book_details_page(request):
    return render(request, "book_details/book_details.html")



def member_registration_page(request):
    return render(request, "member_registration/member_registration.html")

def member_details_page(request):
    return render(request, "member_details/member_details.html")


























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