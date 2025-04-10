from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('', views.user_login, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.user_logout, name='logout'),
]
