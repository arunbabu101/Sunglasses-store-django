from django.shortcuts import render, redirect, get_object_or_404
from .models import Supplier
from .forms import SupplierForm
from shop.models import Reorders
from django.contrib import messages
from django.contrib.auth import authenticate, login
from shop.models import Product
from django.contrib.auth.decorators import login_required

from .forms import SupplierLoginForm

@login_required
def supplier_home(request):
    # Get the logged-in user's supplier profile
    supplier = Supplier.objects.get(user=request.user)
    # Fetch products associated with the supplier
    products = Product.objects.filter(supplier=supplier)
    context = {
        'user': request.user,
        'products': products,
    }
    return render(request, 'supplier_home.html', context)

def supplier_login(request):
    if request.method == 'POST':
        form = SupplierLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                # Redirect to supplier home page on successful login
                return redirect('supplier:supplier_home')  # Use reverse with namespace
            else:
                # Display an error message if login fails
                messages.error(request, 'Invalid email or password.')
    else:
        form = SupplierLoginForm()

    return render(request, 'supplier_login.html', {'form': form})


def display_reorders(request):
    if request.method == 'POST':
        reorder_id = request.POST.get('reorder_id')
        reorder = get_object_or_404(Reorders, id=reorder_id)
        
        if 'send_product' in request.POST:
            reorder.status = 'sent'
            reorder.save()
            messages.success(request, 'Products sent successfully.')
        elif 'cancel_reorder' in request.POST:
            reorder.status = 'canceled'
            reorder.save()
            messages.success(request, 'Reorder canceled successfully.')
        
        return redirect('supplier:display_reorders')

    # Check if the user has a supplier
    if not hasattr(request.user, 'supplier'):
        messages.error(request, "You do not have a supplier account.")
        return redirect('some_other_view')  # Redirect to a suitable page

    # Fetch reorders for the supplier
    reorders = Reorders.objects.filter(supplier=request.user.supplier).exclude(status__in=['sent', 'canceled'])
    
    context = {
        'user': request.user,
        'reorders': reorders,
    }
    return render(request, 'display_reorders.html', context)

def send_product(request, reorder_id):
    reorder = get_object_or_404(Reorders, id=reorder_id)
    reorder.status = 'sent'
    reorder.save()
    messages.success(request, 'Products sent successfully.')
    return redirect('supplier:display_reorders')

def cancel_reorder(request, reorder_id):
    reorder = get_object_or_404(Reorders, id=reorder_id)
    reorder.status = 'canceled'
    reorder.save()
    messages.success(request, 'Reorder canceled successfully.')
    return redirect('supplier:display_reorders')







def supplier_orders(request):
    # Retrieve orders for the current supplier
    supplier_orders = Reorders.objects.filter(supplier=request.user.supplier)
    context = {'supplier_orders': supplier_orders}
    return render(request, 'supplier_orders.html', context)



def previous_reorders(request):
    # Filter previous reorders based on status (sent or canceled)
    previous_sent_reorders = Reorders.objects.filter(status='sent')
    previous_canceled_reorders = Reorders.objects.filter(status='canceled')

    context = {
        'previous_sent_reorders': previous_sent_reorders,
        'previous_canceled_reorders': previous_canceled_reorders,
    }
    return render(request, 'previous_reorders.html', context)