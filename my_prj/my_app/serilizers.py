from rest_framework import serializers
from .models import Parent, Pupil, Book, Rent, User


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = ['parent_id', 'address', 'user']


class PupilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pupil
        fields = ['personal_id', 'full_name', 'grade', 'parent']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['book_id', 'book_name', 'book_grade']


class RentSerializer(serializers.ModelSerializer):
    book_1 = BookSerializer()
    book_2 = BookSerializer()
    book_3 = BookSerializer()
    book_4 = BookSerializer()
    book_5 = BookSerializer()
    book_6 = BookSerializer()
    book_7 = BookSerializer()
    book_8 = BookSerializer()
    book_9 = BookSerializer()
    book_10 = BookSerializer()
    book_11 = BookSerializer()
    book_12 = BookSerializer()
    book_13 = BookSerializer()
    book_14 = BookSerializer()
    book_15 = BookSerializer()
    book_16 = BookSerializer()
    book_17 = BookSerializer()

    class Meta:
        model = Rent
        fields = '__all__'
