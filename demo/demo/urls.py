from django.contrib import admin
from django.urls import path, include
from .index import index_view

urlpatterns = [
    path('', index_view, name="index"),
    path('admin/', admin.site.urls),
    path('sheets/', include('sheets.urls')),
    # Google Auth Views
    path('gauth/', include('django_gauth.urls')),
]
