from django import forms
from datetime import datetime, date
from django.utils.timezone import now
from .models import BookCategory, BookDetails
from django.core.exceptions import ValidationError
import datetime
from .models import Librarian, Member, BookDetails



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
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email =forms.EmailField()
    phone_number = forms.CharField(max_length=25)
    address = forms.CharField(widget=forms.Textarea)
    membership_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    is_active = forms.BooleanField(required=False)

    def clean_membership_date(self):
        membership_date = self.cleaned_data.get("membership_date")
        if membership_date < date.today():
            raise ValidationError("Membership date cannot be in the past.")
        return membership_date

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


class IssueMaintanenceForm(forms.Form):
    librarian_id = forms.ModelChoiceField(queryset=Librarian.objects.all())
    member_id = forms.ModelChoiceField(queryset=Member.objects.all(),required=False)
    book_id = forms.ModelChoiceField(queryset=BookDetails.objects.all())
    fine_cost = forms.IntegerField()
    paid_cost = forms.IntegerField(required=False)
    is_paid = forms.BooleanField(required=False)
    is_return = forms.BooleanField(required=False)