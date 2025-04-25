from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls), # Optional: remove if not used at all
    path('', include('bookstore.urls', namespace='bookstore')),
]