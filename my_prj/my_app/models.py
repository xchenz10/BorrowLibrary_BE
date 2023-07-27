from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


# Create your models here.
class Pupil(models.Model):
    personal_id = models.IntegerField(null=False, blank=False, unique=True)
    full_name = models.CharField(null=False, max_length=50, blank=False)
    grade = models.CharField(null=False, max_length=15, blank=False)
    parent = models.ForeignKey("Parent", on_delete=models.RESTRICT,
                               related_name="parent", null=True)

    class Meta:
        db_table = 'pupil'

    def __str__(self):
        return f'{self.personal_id, self.full_name, self.parent}'


class Parent(models.Model):
    number_rejex = RegexValidator(
        regex=r'^[0-9]+$',
        message="only numbers from 0 to 9 are allowed"
    )

    parent_id = models.CharField(max_length=10, validators=[number_rejex], null=False, blank=False, unique=True)
    address = models.CharField(null=False, blank=False, max_length=75)
    user = models.OneToOneField(User, null=False, blank=False,
                                on_delete=models.RESTRICT, related_name='person_user')

    class Meta:
        db_table = 'parent'

    def __str__(self):
        return f'{self.parent_id, self.user.first_name, self.user.last_name, self.user.email}'


class Book(models.Model):
    book_id = models.CharField(max_length=50, null=False, blank=False, unique=True)
    book_name = models.CharField(max_length=100, null=False, blank=False)
    book_grade = models.CharField(null=False, max_length=15, blank=False)
    value = models.IntegerField(null=True, blank=True, default=1)
    storage = models.IntegerField(null=True, blank=False)

    class Meta:
        db_table = 'Book'

    def __str__(self):
        return f'{self.book_grade} | {self.book_name} |' \
               f'{self.book_id}'


class Rent(models.Model):
    client = models.ForeignKey(Pupil, on_delete=models.RESTRICT,
                               related_name="renter", db_column="client_id")
    start_date = models.DateTimeField(null=False, blank=False)
    end_date = models.DateTimeField(null=False, blank=False)
    book_1 = models.ForeignKey("Book", related_name="rent_book1", on_delete=models.RESTRICT,
                               null=True, blank=True)
    book_2 = models.ForeignKey("Book", related_name="rent_book2", on_delete=models.RESTRICT,
                               blank=True, default=None, null=True)
    book_3 = models.ForeignKey("Book", related_name="rent_book3", on_delete=models.RESTRICT,
                               blank=True, default=None, null=True)
    book_4 = models.ForeignKey("Book", related_name="rent_book4", on_delete=models.RESTRICT,
                               blank=True, default=None, null=True)
    book_5 = models.ForeignKey("Book", related_name="rent_book5", on_delete=models.RESTRICT,
                               blank=True, default=None, null=True)
    book_6 = models.ForeignKey("Book", related_name="rent_book6", on_delete=models.RESTRICT,
                               blank=True, default=None, null=True)
    book_7 = models.ForeignKey("Book", related_name="rent_book7", on_delete=models.RESTRICT,
                               blank=True, default=None, null=True)
    book_8 = models.ForeignKey("Book", related_name="rent_book8", on_delete=models.RESTRICT,
                               blank=True, default=None, null=True)
    book_9 = models.ForeignKey("Book", related_name="rent_book9", on_delete=models.RESTRICT,
                               blank=True, default=None, null=True)
    book_10 = models.ForeignKey("Book", related_name="rent_book10", on_delete=models.RESTRICT,
                                blank=True, default=None, null=True)
    book_11 = models.ForeignKey("Book", related_name="rent_book11", on_delete=models.RESTRICT,
                                blank=True, default=None, null=True)
    book_12 = models.ForeignKey("Book", related_name="rent_book12", on_delete=models.RESTRICT,
                                blank=True, default=None, null=True)
    book_13 = models.ForeignKey("Book", related_name="rent_book13", on_delete=models.RESTRICT,
                                blank=True, default=None, null=True)
    book_14 = models.ForeignKey("Book", related_name="rent_book14", on_delete=models.RESTRICT,
                                blank=True, default=None, null=True)
    book_15 = models.ForeignKey("Book", related_name="rent_book15", on_delete=models.RESTRICT,
                                blank=True, default=None, null=True)
    book_16 = models.ForeignKey("Book", related_name="rent_book16", on_delete=models.RESTRICT,
                                blank=True, default=None, null=True)
    book_17 = models.ForeignKey("Book", related_name="rent_book17", on_delete=models.RESTRICT,
                                blank=True, default=None, null=True)

    class Meta:
        db_table = 'rent'

    def __str__(self):
        return f'Client: {self.client},\n Books:\n ({self.book_1}),\n ({self.book_2}),\n ({self.book_3}),\n' \
               f'({self.book_4}),\n ({self.book_5}),\n ({self.book_6}),\n ' \
               f'({self.book_7}),\n ({self.book_8}),\n ({self.book_9}),\n ({self.book_10}),\n' \
               f' ({self.book_11}),\n ({self.book_12}),\n ({self.book_13})\n' \
               f'-------------------------------------------------------------------------------------\n\n'
