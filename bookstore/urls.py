from django.urls import path
from . import views 

app_name = 'bookstore' 

urlpatterns = [
    
    path('', views.HomeView.as_view(), name='home'),
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('books/<int:book_id>/', views.BookDetailView.as_view(), name='book_detail'), 
    path('register/', views.UserRegistrationView.as_view(), name='register'), 
    path('login/', views.CustomLoginView.as_view(), name='login'), 
    
    path('logout/', views.CustomLogoutView.as_view(), name='logout'), 

    
    path('cart/', views.CartView.as_view(), name='cart_view'),
    path('add-to-cart/<int:book_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('payment/', views.PaymentView.as_view(), name='payment'),

    
    path('manage/books/', views.AdminBookListView.as_view(), name='admin_book_list'),
    path('manage/books/add/', views.AdminBookCreateView.as_view(), name='admin_book_create'),
    path('manage/books/<int:book_id>/edit/', views.AdminBookUpdateView.as_view(), name='admin_book_update'),
    path('manage/books/<int:book_id>/delete/', views.AdminBookDeleteView.as_view(), name='admin_book_delete'),
]