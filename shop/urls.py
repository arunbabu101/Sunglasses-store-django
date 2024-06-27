from django.urls import path
from .import views
from django.contrib.auth import views as auth_views

app_name = 'shop'

urlpatterns = [

    path('', views.allprodcat, name='allprodcat'),
    
    path('change_password/', views.change_password, name='change_password'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.view_profile, name='view_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    path('view_orders/', views.view_orders, name='view_orders'),
    path('shop/return_order/<int:order_id>/', views.return_order, name='return_order'),
    path('submit_return/<int:order_item_id>/', views.submit_return, name='submit_return'),
    path('profile/update_password/', views.update_password, name='update_password'),


    path('delivery_form/', views.delivery_form, name='delivery_form'),

    # path('make_payment/', views.make_payment, name='make_payment'),
    path('bill/<int:order_id>/', views.bill, name='bill'),
    
    path('<slug:c_slug>/<slug:product_slug>/', views.prodetail, name='prodcatdetail'),
    path('<slug:c_slug>/', views.allprodcat, name='products_by_category'),

    path('home/', views.home_view, name='home'),


]
