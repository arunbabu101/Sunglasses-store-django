from django.urls import path
from . import views

app_name = 'supplier' 

urlpatterns = [

    path('', views.supplier_login, name='login_page'),
    path('home/', views.supplier_home, name='supplier_home'),
    path('display_reorders/', views.display_reorders, name='display_reorders'),
    path('send_product/<int:reorder_id>/', views.send_product, name='send_product'),
    path('cancel_reorder/<int:reorder_id>/', views.cancel_reorder, name='cancel_reorder'),
    path('previous_reorders/', views.previous_reorders, name='previous_reorders'),
    
    # Add more URL patterns for other views as needed
]