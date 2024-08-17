from django.urls import path
from . import views

urlpatterns = [
    path('menu-items', views.menu_items),
    path('menu-items/<int:id>', views.single_item),
    path('groups/manager/users',views.managers),
    path('groups/manager/users/<int:id>',views.remove_manager),
    path('groups/delivery-crew/users',views.delivery_crew),
    path('groups/delivery-crew/users/<int:id>',views.remove_delivery_crew),
    path('cart/menu-items',views.cart),
    path('orders',views.orders),
    path('orders/<int:id>',views.single_order),
]