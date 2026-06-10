from rest_framework import serializers
from .models import Users, Member, BookDetails


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = "__all__"

class MemberSerializers(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"

class BookDetailsSerializers(serializers.ModelSerializer):
    class Meta:
        model = BookDetails
        fields = "__all__"