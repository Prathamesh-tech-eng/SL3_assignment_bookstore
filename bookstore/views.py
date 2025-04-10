from django.shortcuts import render, redirect, get_object_or_404
from django.views import View # Using class-based views for structure
from django.contrib.auth.views import LoginView as AuthLoginView # Renaming to avoid conflict
from django.contrib.auth import logout as auth_logout
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin # To protect views
from .models import Book



class HomeView(View):
    def get(self, request, *args, **kwargs):
        
        return render(request, 'bookstore/home.html')

class BookListView(View):
    def get(self, request, *args, **kwargs):
        books = Book.objects.all()
        context = {'books': books}
        
        return render(request, 'bookstore/book_list.html', context)



class CustomLoginView(AuthLoginView):
    template_name = 'bookstore/login.html'
    

def logout_view(request):
    auth_logout(request)
   
    return redirect(reverse('bookstore:home')) # Redirect immediately



class AddToCartView(View):
    def post(self, request, book_id, *args, **kwargs):
        # Get the book or return 404 if not found
        book = get_object_or_404(Book, pk=book_id)

        # Get the cart from the session, or initialize an empty dict if not present
        cart = request.session.get('cart', {})

        # Get current quantity for this book in cart, default to 0 if not there
        current_quantity = cart.get(str(book_id), 0) # Use str(book_id) as session keys must be strings

        # Increment quantity
        cart[str(book_id)] = current_quantity + 1

        # Save the updated cart back into the session
        request.session['cart'] = cart
        request.session.modified = True # Important: Mark session as modified

        # Redirect to the cart view page
        return redirect('bookstore:cart_view')

    def get(self, request, *args, **kwargs):
        
        return redirect('bookstore:book_list')


class CartView(View):
    def get(self, request, *args, **kwargs):
        cart_session = request.session.get('cart', {})
        cart_items = []
        total_price = 0

        for book_id, quantity in cart_session.items():
            try:
                book = Book.objects.get(pk=int(book_id))
                item_total = book.price * quantity
                cart_items.append({
                    'book': book,
                    'quantity': quantity,
                    'item_total': item_total,
                })
                total_price += item_total
            except Book.DoesNotExist:
                
                del request.session['cart'][book_id]
                request.session.modified = True


        context = {
            'cart_items': cart_items,
            'total_price': total_price,
            'is_empty': not bool(cart_items) 
        }
        
        return render(request, 'bookstore/cart.html', context)


class PaymentView(LoginRequiredMixin, View): 
    login_url = reverse_lazy('bookstore:login') 

    def get(self, request, *args, **kwargs):
       
        request.session['cart'] = {}
        request.session.modified = True
        
        return redirect('bookstore:book_list') 