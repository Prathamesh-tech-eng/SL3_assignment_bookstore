from django.urls import path
from . import views # Import views from the current directory

app_name = 'bookstore' # Namespace for URLs

urlpatterns = [
    # User facing URLs
    path('', views.HomeView.as_view(), name='home'),
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('books/<int:book_id>/', views.BookDetailView.as_view(), name='book_detail'), # NEW Book Detail
    path('register/', views.UserRegistrationView.as_view(), name='register'), # NEW Registration
    path('login/', views.CustomLoginView.as_view(), name='login'), # Use CustomLoginView
    # Use POST for logout for better practice, requires a form in template
    path('logout/', views.CustomLogoutView.as_view(), name='logout'), # Use CustomLogoutView

    # Cart URLs
    path('cart/', views.CartView.as_view(), name='cart_view'),
    path('add-to-cart/<int:book_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('payment/', views.PaymentView.as_view(), name='payment'),

    # Custom Admin URLs
    path('manage/books/', views.AdminBookListView.as_view(), name='admin_book_list'),
    path('manage/books/add/', views.AdminBookCreateView.as_view(), name='admin_book_create'),
    path('manage/books/<int:book_id>/edit/', views.AdminBookUpdateView.as_view(), name='admin_book_update'),
    path('manage/books/<int:book_id>/delete/', views.AdminBookDeleteView.as_view(), name='admin_book_delete'),
]