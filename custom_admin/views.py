from django.contrib.auth.models import User
from django.contrib import auth, messages
from .forms import CategoryForm, ProductForm
from django.shortcuts import render, get_object_or_404, redirect
from shop.models import *
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import F 
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import login
from .forms import SupplierForm
from supplier.models import Supplier
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError

# Create your views here.

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('custom_admin:home')
        else:
            return render(request, 'admin_login.html', {'invalid_credentials':'t'})
    return render(request, 'admin_login.html')

def home(request):
    products_list = Product.objects.all()
    category_list = Category.objects.all()
    return render(request, 'admin_home.html', {'categories': category_list, 'products': products_list})

def add_category(request):
    if request.method == 'POST':
        name = request.POST['name']
        slug = request.POST['slug']
        description = request.POST['description']
        image = request.FILES['image']
        new_category = Category(name=name, slug=slug, description=description, image=image)
        new_category.save()
        return redirect('custom_admin:home')
    return render(request, 'add_category.html')

def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('custom_admin:admin_products')  
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})

def edit_category(request, id):
    category = Category.objects.get(id=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)

        if form.is_valid():
            form.save()
            return redirect('custom_admin:edit_category', id)

    else:
        form = CategoryForm(instance=category)
    return render(request, 'edit_category.html', {'category': category, 'form': form})

def edit_product(request, id):
    product = Product.objects.get(id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()
            return redirect('custom_admin:edit_product', id)

    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'product': product, 'form': form})

def delete_category(request, id):
    try:
        category = Category.objects.get(id=id)
        category.delete()
        return JsonResponse({'message': 'Category deleted successfully'})
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)

def delete_product(request, id):
    try:
        product = Product.objects.get(id=id)
        product.delete()
        return JsonResponse({'message': 'Product deleted successfully'})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

def admin_categories(request):
    categories = Category.objects.all()
    return render(request, 'admin_categories.html', {'categories': categories})

def admin_products(request):
    products = Product.objects.all()

    # Check reorder limit for each product and create a list of products reaching the limit
    products_reaching_limit = []
    for product in products:
        if product.stock <= product.reorder:
            products_reaching_limit.append(product)

    # Show notification if any products reach the reorder limit
    if products_reaching_limit:
        products_reaching_limit_url = reverse('custom_admin:products_reaching_limit')
        messages.warning(request, f"{len(products_reaching_limit)} product(s) reach the reorder limit. <a href='{products_reaching_limit_url}'>View Details</a>")

    return render(request, 'admin_products.html', {'products': products, 'products_reaching_limit': products_reaching_limit})

def products_reaching_limit(request):
    products_reaching_limit = Product.objects.filter(stock__lte=F('reorder'))
    return render(request, 'products_reaching_limit.html', {'products': products_reaching_limit})


def admin_view_orders(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('new_status')
        if order_id and new_status:
            order = Order.objects.get(pk=order_id)
            order.status = new_status
            order.save()
            return redirect('custom_admin:admin_view_orders')  # Redirect after saving

    orders = Order.objects.all()
    return render(request, 'admin_view_orders.html', {'orders': orders})

def update_status_processing(request, order_id):
    order = Order.objects.get(pk=order_id)
    order.status = 'processing'
    order.save()
    return redirect('custom_admin:admin_view_orders')  # Redirect to the main orders view

def update_status_shipped(request, order_id):
    order = Order.objects.get(pk=order_id)
    order.status = 'shipped'
    order.save()
    return redirect('custom_admin:admin_view_orders')  # Redirect to the main orders view

def update_status_delivered(request, order_id):
    order = Order.objects.get(pk=order_id)
    order.status = 'delivered'
    order.save()
    return redirect('custom_admin:admin_view_orders') 

def update_status_returned(request, order_id):
    order = Order.objects.get(pk=order_id)
    order.status = 'returned'
    order.save()
    return redirect('custom_admin:admin_view_orders') 


def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'supplier_list.html', {'suppliers': suppliers})

def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                # Check if a user with the given email already exists
                if User.objects.filter(username=email).exists():
                    messages.error(request, 'A user with this email already exists.')
                else:
                    user = User.objects.create_user(username=email, email=email, password=password)
                    supplier = form.save(commit=False)
                    supplier.user = user
                    supplier.status = 'active'  # Ensure status is set
                    supplier.save()
                    messages.success(request, 'Supplier added successfully.')
                    return redirect('custom_admin:supplier_list')
            except IntegrityError:
                messages.error(request, 'An error occurred while creating the supplier.')
    else:
        form = SupplierForm()
    return render(request, 'add_supplier.html', {'form': form})

def edit_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            supplier = form.save(commit=False)
            user = supplier.user
            user.email = form.cleaned_data['email']
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()
            supplier.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('custom_admin:supplier_list')
    else:
        initial_data = {
            'email': supplier.user.email,
            'password': ''
        }
        form = SupplierForm(instance=supplier, initial=initial_data)
    return render(request, 'edit_supplier.html', {'form': form, 'supplier': supplier})



def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        if supplier.product_set.exists():
            messages.error(request, 'Cannot delete supplier. Please update or remove the associated products first.')
        else:
            supplier.user.delete()  # This will also delete the supplier due to the OneToOne relationship
            messages.success(request, 'Supplier deleted successfully.')
        return redirect('custom_admin:supplier_list')
    return render(request, 'confirm_delete.html', {'supplier': supplier})





def reorder_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        pieces = request.POST.get('pieces')
        supplier = product.supplier  # Assuming supplier is related to the product

        # Create a new Reorders instance without setting the status initially
        reorder = Reorders.objects.create(product=product, supplier=supplier, pieces=pieces)

        # Assuming the reorder creation is successful, add a success message
        messages.success(request, 'Reorder placed successfully!')

        # Redirect to admin home page after reorder
        return redirect('custom_admin:admin_products')

    context = {'product': product}
    return render(request, 'reorder_product.html', context)



def reorder_list(request):
    reorders = Reorders.objects.all()

    if request.method == 'POST':
        reorder_id = request.POST.get('reorder_id')
        reorder = Reorders.objects.get(id=reorder_id)
        product = reorder.product
        product.stock = F('stock') + reorder.pieces
        product.save()

        reorder.status = 'updated'
        reorder.save()

    context = {
        'reorders': reorders,
    }
    return render(request, 'reorder_list.html', context)

@csrf_exempt
def add_to_shop(request, reorder_id):
    if request.method == 'POST':
        reorder = get_object_or_404(Reorders, id=reorder_id)
        if reorder.status == 'sent':
            product = reorder.product
            product.stock += reorder.pieces
            product.save()
            # Optionally, you can change the reorder status or delete it
            # reorder.delete()  # If you want to remove the reorder after processing
            reorder.status = 'processed'  # Change the status if you want to keep it
            reorder.save()
        return redirect(reverse('custom_admin:reorder_list'))
    return JsonResponse({'success': False, 'error': 'Invalid request'})




def sales_report_month(request):
    if request.method == 'POST':
        selected_month = request.POST.get('selected_month')
        # Assuming OrderItem model has an 'item_price' field
        product_sales = OrderItem.objects.filter(order__order_date__month=selected_month) \
            .values('product__name', 'product__image') \
            .annotate(total_pieces_sold=Sum('quantity'), total_revenue=Sum('item_price'))
        
        # Calculate total amount by summing total_revenue of all products
        total_amount = sum(item['total_revenue'] for item in product_sales)
        
        context = {
            'selected_month': selected_month,
            'product_sales': product_sales,
            'total_amount': total_amount,  # Add total_amount to context
        }
        return render(request, 'sales_report_month.html', context)
    else:
        return render(request, 'sales_report_month.html', {})

def sales_report_date_range(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        # Assuming Order model has a 'total_amount' field
        sales_within_range = Order.objects.filter(order_date__range=[start_date, end_date]).aggregate(total_sales=Sum('total_amount'))
        context = {
            'start_date': start_date,
            'end_date': end_date,
            'sales_within_range': sales_within_range['total_sales'] if sales_within_range['total_sales'] else 0,
        }
    else:
        context = {}
    return render(request, 'sales_report_date_range.html', context)


def view_returns(request):
    returns = Return.objects.all()
    return render(request, 'view_returns.html', {'returns': returns})