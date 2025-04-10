from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.shortcuts import redirect, get_object_or_404
from .models import Book

# Create your views here.
from django.http import HttpResponse

from .models import Book

def book_list(request):
    books = Book.objects.all()
    return render(request, 'bookstore/book_list.html', {'books': books})




def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse("Invalid credentials")
    return render(request, 'bookstore/login.html')

@login_required
def home(request):
    return render(request, 'bookstore/home.html')

def user_logout(request):
    logout(request)
    return redirect('login')


def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart = request.session.get('cart', [])
    
    cart.append(book_id)
    request.session['cart'] = cart
    request.session.modified = True
    
    return redirect('book_list')


def cart_view(request):
    cart = request.session.get('cart', [])
    books = Book.objects.filter(id__in=cart)
    return render(request, 'bookstore/cart.html', {'cart_books': books})