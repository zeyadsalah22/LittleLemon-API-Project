from django.urls import path
from . import views

urlpatterns = [
    #region function-based views urls
    # path('menu-items', views.menu_items),
    # path('menu-items/<int:id>', views.single_item),
    # path('groups/manager/users',views.managers),
    # path('groups/manager/users/<int:id>',views.remove_manager),
    # path('groups/delivery-crew/users',views.delivery_crew),
    # path('groups/delivery-crew/users/<int:id>',views.remove_delivery_crew),
    # path('cart/menu-items',views.cart),
    # path('orders',views.orders),
    # path('orders/<int:id>',views.single_order),
    #endregion
    
    #region class-based views urls
    path('categories', views.CategoryView.as_view()),
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('groups/manager/users',views.ManagersView.as_view()),
    path('groups/manager/users/<int:pk>',views.RemoveManagerView.as_view()),
    path('groups/delivery-crew/users',views.DeliveryCrewView.as_view()),
    path('groups/delivery-crew/users/<int:pk>',views.RemoveDeliveryCrewView.as_view()),
    path('cart/menu-items',views.CartView.as_view()),
    path('orders',views.OrdersView.as_view()),
    path('orders/<int:pk>',views.SingleOrderView.as_view()),
    #endregion
]