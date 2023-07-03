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
    path('books', views.books),
    path('mk-rent', views.mk_rent),
    path('edit-profile', views.edit_profile),
]
