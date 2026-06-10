from django import forms
from .models import BookCategory
import datetime

CURRENT_YEAR = datetime.datetime.now().year

YEAR_CHOICES = [(year, year) for year in range(1900, CURRENT_YEAR + 1)]

class LoginForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)

class LibrarianFrom(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=25)
    surname = forms.CharField(max_length=25)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)
    is_active = forms.BooleanField(required=False)

class MemberFrom(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=25)
    surname = forms.CharField(max_length=25)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)
    is_active = forms.BooleanField(required=False)

class BookCategoryForm(forms.Form):
    choice = forms.CharField(max_length=100)

class BookForm(forms.Form):
    title = forms.CharField(max_length=255)
    author = forms.CharField(max_length=255)
    category = forms.ModelChoiceField(
        queryset=BookCategory.objects.all(),
        empty_label="Select Category",
        widget=forms.Select(attrs={
            "class": "form-control lms-form-control"
        })
    )
    publication_year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        widget=forms.Select(attrs={"class": "form-control year-select"})
    )
    total_copies = forms.IntegerField()