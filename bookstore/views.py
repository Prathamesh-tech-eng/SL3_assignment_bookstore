from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
# Remove AuthLoginView import
from django.contrib.auth import authenticate, login, logout # Import auth functions
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User # Import User model for registration
from django.contrib import messages # For showing success/error messages
from .models import Book

# --- Basic Views --- (HomeView, BookListView - Keep as is)
class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'bookstore/home.html')

class BookListView(View):
    def get(self, request, *args, **kwargs):
        books = Book.objects.all()
        context = {'books': books}
        return render(request, 'bookstore/book_list.html', context)

# --- NEW: Book Detail View ---
class BookDetailView(View):
    def get(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(Book, pk=book_id)
        context = {'book': book}
        return render(request, 'bookstore/book_detail.html', context)

# --- Authentication Views (Refactored) ---

class UserRegistrationView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('bookstore:book_list') # Redirect logged-in users
        return render(request, 'bookstore/register.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        email = request.POST.get('email') # Optional based on your form
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # --- START: Basic Custom Validation ---
        if not username or not password or not password_confirm:
            messages.error(request, "All fields are required.")
            return render(request, 'bookstore/register.html', {'username': username, 'email': email}) # Pass back input

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'bookstore/register.html', {'username': username, 'email': email})

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
            return render(request, 'bookstore/register.html', {'email': email}) # Don't pass back username if taken

        # Add more validation (email format, password strength) if needed
        # --- END: Basic Custom Validation ---

        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            # You might want to log the user in directly after registration
            login(request, user)
            messages.success(request, "Registration successful! You are now logged in.")
            return redirect('bookstore:book_list') # Redirect to book list or home
        except Exception as e:
            # Log the exception e
            messages.error(request, "An error occurred during registration.")
            return render(request, 'bookstore/register.html', {'username': username, 'email': email})


class CustomLoginView(View): # No longer inherits from Django's LoginView
    template_name = 'bookstore/login.html'
    redirect_authenticated_user = True # Optional: redirect if already logged in

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and self.redirect_authenticated_user:
            redirect_url = request.GET.get('next', reverse('bookstore:book_list'))
            return redirect(redirect_url)
        # Pass 'next' URL to template if present
        context = {'next': request.GET.get('next', '')}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', reverse('bookstore:book_list')) # Get redirect URL

        if not username or not password:
             messages.error(request, "Please enter both username and password.")
             return render(request, self.template_name, {'next': next_url, 'username': username}) # Pass back context

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.info(request, f"Welcome back, {username}!")
            # Redirect to 'next' URL or default
            return redirect(next_url)
        else:
            # Invalid login
            messages.error(request, "Invalid username or password.")
            return render(request, self.template_name, {'next': next_url, 'username': username}) # Pass back context


class CustomLogoutView(View): # Now a CBV
     def post(self, request, *args, **kwargs):
         logout(request)
         messages.success(request, "You have been successfully logged out.")
         # Redirect using settings.LOGOUT_REDIRECT_URL or explicitly
         return redirect(reverse('bookstore:home'))

     def get(self, request, *args, **kwargs):
         # Log out on GET is generally discouraged for security, but can be simple
         # Or redirect GET requests to a confirmation page or just redirect home
         # logout(request)
         # messages.success(request, "You have been successfully logged out.")
         return redirect(reverse('bookstore:home'))


# --- Cart Views --- (AddToCartView, CartView - Keep as is, already CBV & session based)
class AddToCartView(View):
    # ... (keep existing code)
     def post(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(Book, pk=book_id)
        cart = request.session.get('cart', {})
        cart_key = str(book_id) # Use string keys for sessions
        current_quantity = cart.get(cart_key, 0)
        cart[cart_key] = current_quantity + 1
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, f"'{book.title}' added to cart.") # Add feedback
        # Decide where to redirect - cart or back to list? Let's go to cart.
        return redirect('bookstore:cart_view')

    def get(self, request, *args, **kwargs):
         # Don't allow adding via GET
        return redirect('bookstore:book_list')

class CartView(View):
    # ... (keep existing code)
    def get(self, request, *args, **kwargs):
        cart_session = request.session.get('cart', {})
        cart_items = []
        total_price = 0

        books_to_fetch = [int(book_id) for book_id in cart_session.keys()]
        books_in_db = Book.objects.filter(pk__in=books_to_fetch).in_bulk() # Efficient fetch

        ids_to_remove_from_session = []

        for book_id_str, quantity in cart_session.items():
            book_id = int(book_id_str)
            book = books_in_db.get(book_id) # Get book from prefetched dict

            if book and quantity > 0:
                item_total = book.price * quantity
                cart_items.append({
                    'book': book,
                    'quantity': quantity,
                    'item_total': item_total,
                })
                total_price += item_total
            else:
                # Book removed from DB or invalid quantity - mark for removal from session
                ids_to_remove_from_session.append(book_id_str)

        # Clean up session if necessary
        if ids_to_remove_from_session:
            cart_modified = False
            for book_id_str in ids_to_remove_from_session:
                if book_id_str in request.session['cart']:
                    del request.session['cart'][book_id_str]
                    cart_modified = True
            if cart_modified:
                request.session.modified = True


        context = {
            'cart_items': cart_items,
            'total_price': total_price,
            'is_empty': not bool(cart_items)
        }
        return render(request, 'bookstore/cart.html', context)

# --- Payment View --- (Keep as is for simulation, ensure LoginRequiredMixin is used)
class PaymentView(LoginRequiredMixin, View):
    login_url = reverse_lazy('bookstore:login')
    def get(self, request, *args, **kwargs):
        request.session['cart'] = {}
        request.session.modified = True
        messages.success(request, 'Payment successful (simulation)! Your cart is cleared.')
        return redirect('bookstore:book_list')

# --- ============================ ---
# --- Custom Admin Panel Views ---
# --- ============================ ---

class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure user is staff or superuser."""
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        # Optionally add a message
        messages.error(self.request, "You do not have permission to access this page.")
        # Redirect to login or home page
        if not self.request.user.is_authenticated:
            return redirect('%s?next=%s' % (reverse('bookstore:login'), self.request.path))
        return redirect(reverse('bookstore:home'))


class AdminBookListView(StaffRequiredMixin, View):
    template_name = 'bookstore/admin/admin_book_list.html'

    def get(self, request, *args, **kwargs):
        books = Book.objects.all().order_by('title')
        context = {'books': books}
        return render(request, self.template_name, context)


class AdminBookCreateView(StaffRequiredMixin, View):
    template_name = 'bookstore/admin/admin_book_form.html'

    def get(self, request, *args, **kwargs):
        # Pass empty context for a new form
        return render(request, self.template_name, {'action_name': 'Create'})

    def post(self, request, *args, **kwargs):
        title = request.POST.get('title')
        author = request.POST.get('author')
        description = request.POST.get('description', '') # Optional field
        price_str = request.POST.get('price')

        # --- Basic Custom Validation ---
        errors = {}
        if not title: errors['title'] = "Title is required."
        if not author: errors['author'] = "Author is required."
        if not price_str:
            errors['price'] = "Price is required."
        else:
            try:
                price = float(price_str) # Use Decimal later for precision
                if price < 0: errors['price'] = "Price cannot be negative."
            except ValueError:
                errors['price'] = "Invalid price format."

        if errors:
             messages.error(request, "Please correct the errors below.")
             # Pass errors and original data back to template
             context = {
                 'errors': errors,
                 'book_data': request.POST, # Pass POST data back
                 'action_name': 'Create'
             }
             return render(request, self.template_name, context)
        # --- End Validation ---

        try:
            Book.objects.create(
                title=title,
                author=author,
                description=description,
                price=price # Use Decimal(price_str) if using DecimalField
            )
            messages.success(request, f"Book '{title}' created successfully.")
            return redirect('bookstore:admin_book_list')
        except Exception as e:
             # Log e
             messages.error(request, "An error occurred while creating the book.")
             context = {
                 'errors': {'general': 'An unexpected error occurred.'},
                 'book_data': request.POST,
                 'action_name': 'Create'
             }
             return render(request, self.template_name, context)


class AdminBookUpdateView(StaffRequiredMixin, View):
    template_name = 'bookstore/admin/admin_book_form.html'

    def get(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(Book, pk=book_id)
        context = {'book': book, 'action_name': 'Update'}
        return render(request, self.template_name, context)

    def post(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(Book, pk=book_id)
        title = request.POST.get('title')
        author = request.POST.get('author')
        description = request.POST.get('description', '')
        price_str = request.POST.get('price')

        # --- Basic Custom Validation (similar to Create) ---
        errors = {}
        if not title: errors['title'] = "Title is required."
        if not author: errors['author'] = "Author is required."
        if not price_str: errors['price'] = "Price is required."
        else:
            try:
                price = float(price_str)
                if price < 0: errors['price'] = "Price cannot be negative."
            except ValueError:
                errors['price'] = "Invalid price format."

        if errors:
             messages.error(request, "Please correct the errors below.")
             context = {
                 'errors': errors,
                 'book_data': request.POST, # Pass POST data
                 'book': book, # Pass original book object for ID etc.
                 'action_name': 'Update'
             }
             return render(request, self.template_name, context)
        # --- End Validation ---

        try:
            book.title = title
            book.author = author
            book.description = description
            book.price = price # Use Decimal(price_str) if using DecimalField
            book.save()
            messages.success(request, f"Book '{book.title}' updated successfully.")
            return redirect('bookstore:admin_book_list')
        except Exception as e:
             # Log e
             messages.error(request, "An error occurred while updating the book.")
             context = {
                 'errors': {'general': 'An unexpected error occurred.'},
                 'book_data': request.POST,
                 'book': book,
                 'action_name': 'Update'
             }
             return render(request, self.template_name, context)


class AdminBookDeleteView(StaffRequiredMixin, View):
    template_name = 'bookstore/admin/admin_book_confirm_delete.html'

    def get(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(Book, pk=book_id)
        context = {'book': book}
        return render(request, self.template_name, context)

    def post(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(Book, pk=book_id)
        book_title = book.title # Get title before deleting
        try:
            book.delete()
            messages.success(request, f"Book '{book_title}' deleted successfully.")
            return redirect('bookstore:admin_book_list')
        except Exception as e:
             # Log e
             messages.error(request, "An error occurred while deleting the book.")
             # Redirect back to list or show error on confirmation page?
             context = {'book': book, 'error': 'Deletion failed.'}
             return render(request, self.template_name, context)