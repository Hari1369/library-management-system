from django.db import models


class Librarian(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    is_shown = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "librarian_details"
    def __str__(self):
        return f"({self.username}) ({self.name}) ({self.surname}) ({self.email}) ({self.phone_number}) ({self.address}) ({self.is_active}) ({self.created_at}) ({self.updated_at})"


class BookCategory(models.Model):
    choice = models.CharField(max_length=100, unique=True)
    class Meta:
        db_table = "book_category"
    def __str__(self):
        return self.choice


class BookDetails(models.Model):
    isbn = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255, unique=True)
    author = models.CharField(max_length=255)
    category = models.ForeignKey(BookCategory, on_delete=models.CASCADE)
    publication_year = models.IntegerField()
    total_copies = models.IntegerField()
    available_copies = models.IntegerField()
    is_acitve = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "book_details"
    def __str__(self):
        return f"({self.isbn}) ({self.title}) ({self.author}) ({self.category}) ({self.publication_year}) ({self.total_copies}) ({self.available_copies}) ({self.created_at}) ({self.updated_at})"


class Member(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    membership_date = models.DateField()
    is_active = models.BooleanField(default=True)
    is_expired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "member_detail"
    def __str__(self):
        return  f"{self.name} ({self.email}) ({self.phone_number}) ({self.address}) ({self.member_detail}) ({self.is_active}) ({self.created_at}) ({self.updated_at})"


class IssueMaintanence(models.Model):
    librarian = models.ForeignKey(Librarian, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)
    book = models.ForeignKey(BookDetails, on_delete=models.CASCADE)
    books_number = models.IntegerField(default=1)
    issue_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "issue_maintanence"
    def __str__(self):
        return f"{self.librarian} {self.book} {self.books_number} {self.issue_date} {self.due_date} {self.status}"


class FineMaintanence(models.Model):
    librarian = models.ForeignKey(Librarian, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)
    book = models.ForeignKey(BookDetails, on_delete=models.CASCADE)
    fine_cost = models.IntegerField()
    paid_cost = models.IntegerField(null=True)
    overdue_date = models.DateField(null=True, blank=True)
    books_number = models.IntegerField(default=1)
    is_paid = models.BooleanField(default=False)
    is_return = models.BooleanField(default=False) 
    paid_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "fine_maintanence"
    def __str__(self):
        return f"({self.librarian}) ({self.book}) ({self.fine_cost}) ({self.paid_cost}) ({self.books_number}) ({self.is_paid}) ({self.paid_time}) ({self.created_at}) ({self.updated_at})"


class NotificationRecord(models.Model):
    user = models.ForeignKey(Member, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    class Meta:
        db_table = "notifications"
    def __str__(self):
        return f"({self.user}) ({self.message}) ({self.created_at}) ({self.status})"