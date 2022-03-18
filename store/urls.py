from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('register/', views.register, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('all_products/', views.all_products, name='all_products'),
    path('delete_product/<int:id>//', views.delete_product, name='delete_product'),
    path('all_products_admin/', views.all_products_admin,
         name='all_products_admin'),
    path('view_product/<int:id>/', views.view_product, name='view_product'),
    path('update_product/<int:id>/', views.update_product, name='update_product'),


]
