from django.urls import path
from . import views
app_name = 'custom_admin'

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('home/', views.home, name='home'),
    path('sales/report/monthly/', views.sales_report_month, name='sales_report_month'),
    path('sales/report/date-range/', views.sales_report_date_range, name='sales_report_date_range'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_category/<int:id>', views.edit_category, name='edit_category'),
    path('reorder-product/<int:product_id>/', views.reorder_product, name='reorder_product'),
    path('edit_product/<int:id>', views.edit_product, name='edit_product'),
    path('delete_category/<int:id>', views.delete_category, name='delete_category'),
    path('delete_product/<int:id>', views.delete_product, name='delete_product'),
    path('admin_categories/', views.admin_categories, name='admin_categories'),
    path('admin_products/', views.admin_products, name='admin_products'),
    path('products/reaching-limit/', views.products_reaching_limit, name='products_reaching_limit'),
    path('custom_admin/admin/orders/', views.admin_view_orders, name='admin_view_orders'),
    path('update_status/processing/<int:order_id>/', views.update_status_processing, name='update_status_processing'),
    path('update_status/shipped/<int:order_id>/', views.update_status_shipped, name='update_status_shipped'),
    path('update_status/delivered/<int:order_id>/', views.update_status_delivered, name='update_status_delivered'),
    path('update_status/returned/<int:order_id>/', views.update_status_returned, name='update_status_returned'),
    path('admin/view_returns/', views.view_returns, name='view_returns'),

    path('add_supplier/', views.add_supplier, name='add_supplier'),
    path('suppliers/edit/<int:supplier_id>/', views.edit_supplier, name='edit_supplier'),
    path('suppliers/delete/<int:supplier_id>/', views.delete_supplier, name='delete_supplier'),
    path('list/', views.supplier_list, name='supplier_list'), 
    path('reorder-list/', views.reorder_list, name='reorder_list'),
    path('add_to_shop/<int:reorder_id>/', views.add_to_shop, name='add_to_shop'),


]