from django.contrib import admin
from .models import Parent, Pupil, User, Book, Rent

# from django.contrib.sessions import

admin.site.register(Pupil)
admin.site.register(Parent)
admin.site.register(Rent)
admin.site.register(Book)

# admin.site.register(Sessions)
