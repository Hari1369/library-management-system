from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Users, Member, BookDetails, BookCategory
from .serializers import UserSerializers, MemberSerializers
import json



def log_in_page(request):
    return render(request, "log_in/log_in.html")

def librarian_registration_page(request):
    return render(request, "librarians_registration/librarians_registration.html")

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