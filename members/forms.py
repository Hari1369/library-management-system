from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)


class UserFrom(forms.Form):
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


class BookFrom(forms.Form):
    title = forms.CharField(max_length=255)
    author = forms.CharField(max_length=255)
    publication_year = forms.IntegerField()
    total_copies = forms.IntegerField()
    available_copies = forms.IntegerField()