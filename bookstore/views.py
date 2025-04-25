from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from django.urls import reverse_lazy, reverse
from django.conf import settings 
from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Book



class HomeView(View):
    """Displays the home page."""
    def get(self, request, *args, **kwargs):
        return render(request, 'bookstore/home.html')

class BookListView(View):
    """Displays the list of available books."""
    def get(self, request, *args, **kwargs):
        books = Book.objects.all().order_by('title') 
        context = {'books': books}
        return render(request, 'bookstore/book_list.html', context)

class BookDetailView(View):
    """Displays the details of a single book."""
    def get(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(Book, pk=book_id)
        context = {'book': book}
        return render(request, 'bookstore/book_detail.html', context)



class UserRegistrationView(View):
    """Handles user registration."""
    template_name = 'bookstore/register.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('bookstore:book_list') 
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', '').strip() 
        email = request.POST.get('email', '').strip() 
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        
        if not username or not password or not password_confirm:
            messages.error(request, "Username and password fields are required.")
            return render(request, self.template_name, {'username': username, 'email': email})

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, self.template_name, {'username': username, 'email': email})

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
            return render(request, self.template_name, {'email': email})

        

        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            login(request, user) 
            messages.success(request, f"Registration successful! Welcome, {username}.")
            return redirect(settings.LOGIN_REDIRECT_URL) 
        except Exception as e:
            
            messages.error(request, "An error occurred during registration. Please try again.")
            return render(request, self.template_name, {'username': username, 'email': email})

class CustomLoginView(View):
    """Handles user login using manual form handling."""
    template_name = 'bookstore/login.html'
    redirect_authenticated_user = True

    def get(self, request, *args, **kwargs):
        next_url = request.GET.get('next', '')
        if request.user.is_authenticated and self.redirect_authenticated_user:
            
            redirect_url = next_url if next_url else settings.LOGIN_REDIRECT_URL
            return redirect(redirect_url)
        
        context = {'next': next_url}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')
        
        next_url_from_post = request.POST.get('next', '')

        if not username or not password:
             messages.error(request, "Please enter both username and password.")
             
             return render(request, self.template_name, {'next': next_url_from_post, 'username': username})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.info(request, f"Welcome back, {username}!")
            
            
            redirect_to = next_url_from_post if next_url_from_post else settings.LOGIN_REDIRECT_URL

            
            
            
            
            

            return redirect(redirect_to)
        else:
            
            messages.error(request, "Invalid username or password.")
            
            return render(request, self.template_name, {'next': next_url_from_post, 'username': username})


class CustomLogoutView(View):
    """Handles user logout."""
    def post(self, request, *args, **kwargs):
        
        logout(request)
        messages.success(request, "You have been successfully logged out.")
        return redirect(settings.LOGOUT_REDIRECT_URL) 

    def get(self, request, *args, **kwargs):
        
        
        logout(request)
        messages.success(request, "You have been successfully logged out.")
        return redirect(settings.LOGOUT_REDIRECT_URL)



class AddToCartView(View):
    """Adds a book to the shopping cart stored in the session."""
    def post(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(Book, pk=book_id)
        
        cart = request.session.get('cart', {})
        cart_key = str(book_id) 
        current_quantity = cart.get(cart_key, 0)
        cart[cart_key] = current_quantity + 1
        request.session['cart'] = cart 
        request.session.modified = True 
        messages.success(request, f"'{book.title}' added to cart.")
        
        return redirect('bookstore:cart_view')

    def get(self, request, *args, **kwargs):
         
        messages.warning(request, "Invalid action.")
        return redirect('bookstore:book_list')

class CartView(View):
    """Displays the items currently in the shopping cart."""
    template_name = 'bookstore/cart.html'

    def get(self, request, *args, **kwargs):
        cart_session = request.session.get('cart', {})
        cart_items = []
        total_price = 0.0
        ids_to_remove_from_session = []

        
        book_ids = [int(book_id) for book_id in cart_session.keys() if book_id.isdigit()]
        books_in_db = Book.objects.filter(pk__in=book_ids).in_bulk() 

        for book_id_str, quantity in cart_session.items():
            try:
                book_id = int(book_id_str)
                book = books_in_db.get(book_id) 

                if book and isinstance(quantity, int) and quantity > 0:
                    item_total = float(book.price) * quantity 
                    cart_items.append({
                        'book': book,
                        'quantity': quantity,
                        'item_total': item_total,
                    })
                    total_price += item_total
                else:
                    
                    ids_to_remove_from_session.append(book_id_str)
            except (ValueError, TypeError):
                
                 ids_to_remove_from_session.append(book_id_str)


        
        if ids_to_remove_from_session:
            cart_modified = False
            current_cart = request.session.get('cart', {}) 
            for book_id_str in ids_to_remove_from_session:
                if book_id_str in current_cart:
                    del current_cart[book_id_str]
                    cart_modified = True
            if cart_modified:
                request.session['cart'] = current_cart 
                request.session.modified = True


        context = {
            'cart_items': cart_items,
            'total_price': total_price,
            'is_empty': not bool(cart_items) 
        }
        return render(request, self.template_name, context)



class PaymentView(LoginRequiredMixin, View):
    """Simulates a payment process by clearing the cart."""
    login_url = reverse_lazy('bookstore:login') 

    def get(self, request, *args, **kwargs):
        
        
        if 'cart' in request.session:
            request.session['cart'] = {}
            request.session.modified = True
            messages.success(request, 'Payment successful (simulation)! Your cart has been cleared.')
        else:
             messages.info(request, 'Your cart was already empty.')
        return redirect('bookstore:book_list')





class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure user is logged in and is a staff member."""
    login_url = reverse_lazy('bookstore:login') 

    def test_func(self):
        
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        
        if not self.request.user.is_authenticated:
            
            return redirect(f"{self.login_url}?next={self.request.path}")
        else:
            
            messages.error(self.request, "You do not have permission to access this admin area.")
            return redirect(reverse('bookstore:home'))


class AdminBookListView(StaffRequiredMixin, View):
    """Displays list of books for admin management."""
    template_name = 'bookstore/admin/admin_book_list.html'

    def get(self, request, *args, **kwargs):
        books = Book.objects.all().order_by('title')
        context = {'books': books}
        return render(request, self.template_name, context)


class AdminBookCreateView(StaffRequiredMixin, View):
    """Handles creation of new books by admin."""
    template_name = 'bookstore/admin/admin_book_form.html'

    def get(self, request, *args, **kwargs):
        
        context = {'action_name': 'Create'}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        description = request.POST.get('description', '').strip()
        price_str = request.POST.get('price', '').strip()
        price = None 

        
        errors = {}
        if not title: errors['title'] = "Title is required."
        if not author: errors['author'] = "Author is required."
        if not price_str:
            errors['price'] = "Price is required."
        else:
            try:
                
                price = float(price_str)
                if price < 0: errors['price'] = "Price cannot be negative."
            except ValueError:
                errors['price'] = "Invalid price format (e.g., 12.99)."

        if errors:
             messages.error(request, "Please correct the errors below.")
             
             context = {
                 'errors': errors,
                 'book_data': request.POST, 
                 'action_name': 'Create'
             }
             return render(request, self.template_name, context)

        
        try:
            Book.objects.create(
                title=title,
                author=author,
                description=description,
                price=price 
            )
            messages.success(request, f"Book '{title}' created successfully.")
            return redirect('bookstore:admin_book_list')
        except Exception as e:
             
             messages.error(request, "An error occurred while creating the book.")
             context = {
                 'errors': {'general': 'An unexpected error occurred.'}, 
                 'book_data': request.POST,
                 'action_name': 'Create'
             }
             return render(request, self.template_name, context)


class AdminBookUpdateView(StaffRequiredMixin, View):
    """Handles updating existing books by admin."""
    template_name = 'bookstore/admin/admin_book_form.html'

    def get(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(Book, pk=book_id)
        
        context = {'book': book, 'action_name': 'Update'}
        return render(request, self.template_name, context)

    def post(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(Book, pk=book_id)
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        description = request.POST.get('description', '').strip()
        price_str = request.POST.get('price', '').strip()
        price = None

        
        errors = {}
        if not title: errors['title'] = "Title is required."
        if not author: errors['author'] = "Author is required."
        if not price_str:
            errors['price'] = "Price is required."
        else:
            try:
                price = float(price_str)
                if price < 0: errors['price'] = "Price cannot be negative."
            except ValueError:
                errors['price'] = "Invalid price format (e.g., 12.99)."

        if errors:
             messages.error(request, "Please correct the errors below.")
             context = {
                 'errors': errors,
                 'book_data': request.POST, 
                 'book': book, 
                 'action_name': 'Update'
             }
             return render(request, self.template_name, context)

        
        try:
            book.title = title
            book.author = author
            book.description = description
            book.price = price 
            book.save() 
            messages.success(request, f"Book '{book.title}' updated successfully.")
            return redirect('bookstore:admin_book_list')
        except Exception as e:
             
             messages.error(request, "An error occurred while updating the book.")
             context = {
                 'errors': {'general': 'An unexpected error occurred.'},
                 'book_data': request.POST,
                 'book': book,
                 'action_name': 'Update'
             }
             return render(request, self.template_name, context)


class AdminBookDeleteView(StaffRequiredMixin, View):
    """Handles deletion of books by admin."""
    template_name = 'bookstore/admin/admin_book_confirm_delete.html'

    def get(self, request, book_id, *args, **kwargs):
        
        book = get_object_or_404(Book, pk=book_id)
        context = {'book': book}
        return render(request, self.template_name, context)

    def post(self, request, book_id, *args, **kwargs):
        
        book = get_object_or_404(Book, pk=book_id)
        book_title = book.title 
        try:
            book.delete()
            messages.success(request, f"Book '{book_title}' deleted successfully.")
            return redirect('bookstore:admin_book_list')
        except Exception as e:
             
             messages.error(request, f"An error occurred while deleting the book '{book_title}'.")
             
             return redirect('bookstore:admin_book_list')