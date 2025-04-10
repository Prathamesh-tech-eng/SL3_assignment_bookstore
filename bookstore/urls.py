from django.urls import path
from . import views # Import views from the current directory

app_name = 'bookstore' # Namespace for URLs

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'), 
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('login/', views.CustomLoginView.as_view(), name='login'), 
    path('logout/', views.logout_view, name='logout'), 
    path('cart/', views.CartView.as_view(), name='cart_view'), 
    # book_id is passed in the URL for adding to cart
    path('add-to-cart/<int:book_id>/', views.AddToCartView.as_view(), name='add_to_cart'), 
    path('payment/', views.PaymentView.as_view(), name='payment'), 
]