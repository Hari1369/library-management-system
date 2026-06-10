from rest_framework import serializers
from .models import Librarian, Member, BookDetails


class LibrarianSerializers(serializers.ModelSerializer):
    class Meta:
        model = Librarian
        fields = "__all__"

class MemberSerializers(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"

class BookDetailsSerializers(serializers.ModelSerializer):
    class Meta:
        model = BookDetails
        fields = "__all__"