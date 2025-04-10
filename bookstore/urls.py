from django.urls import path
from . import views
from .views import payment_view

urlpatterns = [
    path('', views.user_login, name='login'),  # root URL shows login page
    path('home/', views.home, name='home'),
    path('logout/', views.user_logout, name='logout'),
    path('books/', views.book_list, name='book_list'),
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('payment/', payment_view, name='payment'),
]
