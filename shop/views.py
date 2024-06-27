from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from .models import *
from .forms import *
from cart.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from django.http import Http404
from django.contrib import messages
from cart.views import _cart_id
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


def allprodcat(request, c_slug=None):
    c_page = None
    products_list = None
    if c_slug is not None:
        c_page = get_object_or_404(Category, slug=c_slug)
        products_list = Product.objects.all().filter(category=c_page, available=True)
    else:
        products_list = Product.objects.all().filter(available=True)
    
    paginator = Paginator(products_list, 32)  # 8 rows x 4 products per row = 32 products per page
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    try:
        products = paginator.page(page)
    except (EmptyPage, InvalidPage):
        products = paginator.page(paginator.num_pages)
    
    return render(request, "category.html", {'category': c_page, 'products': products})

def prodetail(request, c_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=c_slug, slug=product_slug)
        # Fetch products from the same supplier
        related_products = Product.objects.filter(supplier=product.supplier).exclude(id=product.id)[:4]
    except Product.DoesNotExist:
        raise Http404("Product does not exist")
    return render(request, 'product.html', {'product': product, 'related_products': related_products})


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(username=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Login successful')
            return redirect('shop:allprodcat')
        else:
            messages.error(request, 'Invalid login credentials')
            return render(request, 'login.html', {'invalid_credentials': 't'})
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        # Custom validation for email uniqueness
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in use.')
        else:
            # Custom validation for password complexity
            if not any(char.isupper() for char in password):
                messages.error(request, 'Password must contain at least one uppercase letter.')
            elif not any(char.islower() for char in password):
                messages.error(request, 'Password must contain at least one lowercase letter.')
            elif not any(char.isdigit() for char in password):
                messages.error(request, 'Password must contain at least one digit.')
            elif password != confirm_password:
                messages.error(request, 'Passwords do not match.')
            else:
                user = User.objects.create_user(
                    username=email,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password
                )
                user.save()

                # Send a welcome email
                subject = 'Welcome to Ray-Ban Store!'
                message = f"""
                Dear {first_name},

                Welcome to Ray-Ban Store!

                Thank you for registering with us. Your account has been successfully created.

                Here are your account details:
                - Username: {email}
                - First Name: {first_name}
                - Last Name: {last_name}

                We are excited to have you as part of our community. You can now log in to your account using the email and password you provided during registration.

                If you have any questions or need assistance, feel free to contact our support team.

                Best regards,
                Ray-Ban Team

                arun.23pmc@mariancollege.org | +91 6282426640
                """
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email]
                send_mail(subject, message, email_from, recipient_list)

                return redirect('shop:login')  # Redirect to your login view

    return render(request, 'register.html')

def logout_view(request):
    auth.logout(request)
    return redirect('shop:allprodcat')


def user(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-order_date')  # Filter orders for the logged-in user

    return render(request, "user.html", {'orders':orders})


def home_view(request):
    return render(request, 'home.html')


def delivery_form(request):
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():  # Use transaction.atomic to ensure atomicity of database operations
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    cart_items = CartItem.objects.filter(cart=cart, active=True)
                    total = 0
                    for cart_item in cart_items:
                        subtotal = cart_item.sub_total()
                        total += subtotal
                        product = cart_item.product
                        product.stock -= cart_item.quantity
                        product.save()
                        cart_item.delete()

                    # Create the order after processing cart items
                    order = Order.objects.create(
                        user=request.user,
                        total_amount=total,
                        # Add other fields as needed
                    )
                    for cart_item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            quantity=cart_item.quantity,
                            item_price=cart_item.product.price  # Assuming item_price is stored in the Product model
                        )

                    # Compose email content
                    email_subject = 'Order Confirmation'
                    email_body = f"Dear {form.cleaned_data['first_name']} {form.cleaned_data['last_name']},\n\n"
                    email_body += "Thank you for your purchase! Here are the details of your order:\n\n"
                    for cart_item in cart_items:
                        email_body += f"Product: {cart_item.product.name}\n"
                        email_body += f"Quantity: {cart_item.quantity}\n"
                        email_body += f"Price: ${cart_item.product.price}\n\n"
                    email_body += f"Total Amount: ${total}\n\n"
                    email_body += "Your order will be delivered to the following address:\n"
                    email_body += f"{form.cleaned_data['street_address']}\n"
                    email_body += f"{form.cleaned_data['city']}, {form.cleaned_data['postal_code']}\n"
                    email_body += f"{form.cleaned_data['country']}\n\n"
                    email_body += "Thank you for shopping with us!\n\n"
                    email_body += "Best regards,\nRay-Ban"

                    # Send email
                    send_mail(
                        email_subject,
                        email_body,
                        settings.DEFAULT_FROM_EMAIL,
                        [form.cleaned_data['email']],
                        fail_silently=False,
                    )

                    return render(request, 'bill.html', {'form': form.cleaned_data, 'cart_items': cart_items, 'total': total})
            except ObjectDoesNotExist:
                pass

    else:
        form = DeliveryForm()

    return render(request, 'delivery_form.html', {'form': form})
# def delivery_form(request):
#     if request.method == 'POST':
#         form = DeliveryForm(request.POST)
#         if form.is_valid():
#             try:
#                 cart = Cart.objects.get(cart_id=_cart_id(request))
#                 cart_items = CartItem.objects.filter(cart=cart, active=True)
#                 total = 0
#                 for cart_item in cart_items:
#                     # Ensure cart_item.sub_total is a numerical value
#                     subtotal = cart_item.sub_total()
#                     total += subtotal
#                     # Reduce product quantity from stock
#                     product = cart_item.product
#                     product.stock -= cart_item.quantity
#                     product.save()
#                     # Optionally, you can delete cart items after processing
#                     cart_item.delete()
#             except ObjectDoesNotExist:
#                 pass

#             # Pass the form data, cart items, and total amount to the template
#             return render(request, 'bill.html', {'form': form.cleaned_data, 'cart_items': cart_items, 'total': total})
#     else:
#         form = DeliveryForm()

#     return render(request, 'delivery_form.html', {'form': form})




def bill(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    return render(request, 'bill.html', {'order': order, 'order_items': order_items})

def view_orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-order_date')
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    return render(request, 'view_orders.html', {'user_orders': user_orders, 'now': now, 'thirty_days_ago': thirty_days_ago})

def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    if order.status == 'delivered' and order.order_date > thirty_days_ago:
        order_item = order.items.first()  # Assuming only one item per order for simplicity
        if request.method == 'POST':
            form = ReturnForm(request.POST)
            if form.is_valid():
                return_instance = form.save(commit=False)
                return_instance.order_item = order_item
                return_instance.save()
                return HttpResponse("Return request submitted successfully.")
        else:
            form = ReturnForm()
        return render(request, 'return_order.html', {'order_item': order_item, 'form': form})
    else:
        return HttpResponse("Order is not eligible for return.")

def submit_return(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    if request.method == 'POST':
        reason = request.POST.get('reason')
        # Process the return logic here (e.g., update order status, create return record, etc.)
        # Redirect to a success page or order details page
        return redirect('order_details', order_id=order_item.order.id)  # Assuming order_details is a view for order details
    return redirect('shop:view_orders')  # Redirect to orders page if not a POST request


def view_profile(request):
    return render(request, 'view_profile.html')

def update_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile:view_profile')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'update_password.html', {'form': form})



def change_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if username exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Invalid username. Please try again.')
            return redirect('shop:change_password')

        # Check if new password and confirm password match
        if new_password != confirm_password:
            messages.error(request, 'New password and confirm password do not match.')
            return redirect('shop:change_password')

        # Update user's password
        user.password = make_password(new_password)
        user.save()

        messages.success(request, 'Password changed successfully!')
        return redirect('shop:login')

    return render(request, 'change_password.html')




from django.contrib.auth import logout
@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        new_password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if new_password != '' and new_password == confirm_password:
            user.set_password(new_password)
        else:
            messages.error(request, "Passwords do not match or password field is empty.")

        user.save()
        messages.success(request, 'Profile updated successfully. Please log in again with your new credentials.')

        # Log out the user
        logout(request)

        # Redirect to the login page
        return redirect('shop:login')

    return render(request, 'edit_profile.html', {'user': request.user})



def about_us(request):
    return render(request, 'footer/about-us.html')


def filter_by_price(request):
    max_price = request.GET.get('price', 100000)  # Default to max 1000 if not provided
    products = Product.objects.filter(price__lte=max_price, available=True)
    
    return render(request, 'home.html', {'products': products})