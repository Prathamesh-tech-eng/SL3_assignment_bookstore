from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def book_list(request):
    return HttpResponse("Welcome to the Bookstore!")

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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
