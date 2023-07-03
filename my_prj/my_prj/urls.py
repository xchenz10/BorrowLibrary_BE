from django.contrib import admin
from django.urls import path, include

urlpatterns = [
   path('admin/', admin.site.urls),
   path('app/', include('my_app.urls')),
   path('api/v1/', include('my_app.urls_api')),

]
