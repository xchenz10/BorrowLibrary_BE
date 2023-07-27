from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', views.home),
    path('sign-up', views.signup),
    path('login', obtain_auth_token),
    path('check-token', views.check_token),
    path('create-pupil', views.create_pupil),
    path('has-rent', views.has_rent),
    path('books1', views.books_for_rent),
    path('mk-rent', views.mk_rent),
    path('edit-profile', views.edit_profile),
    path('send-email', views.send_email),
    path('book-value', views.book_value),
    path('books2', views.dash_books),
    path('rents', views.dash_rents),
    path('dash-client-rent', views.dash_client_rent),
    path('check-superuser', views.check_superuser),
    path('contact-msg', views.contact_msg),
]
