from django.shortcuts import render,get_object_or_404
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status,generics
from rest_framework.decorators import api_view, permission_classes,throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .permissions import *
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .throttles import *
from django.core.paginator import Paginator, EmptyPage
from .models import *
from .serializers import *
from datetime import date

#region Function-based views

@api_view(['GET','POST'])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAuthenticated])
def menu_items(request):
    if request.method == 'GET':
            items = MenuItem.objects.select_related('category').all()
            category_name = request.query_params.get('category')
            to_price = request.query_params.get('to_price')
            search = request.query_params.get('search')
            ordering = request.query_params.get('ordering')
            per_page = request.query_params.get('perpage',default=4)
            page = request.query_params.get('page',default=1)
            if category_name:
                items = items.filter(category__title__icontains=category_name)
            if to_price:
                items = items.filter(price__lte=to_price)
            if search:
                items = items.filter(title__icontains=search)
            if ordering:
                ordering = ordering.split(',')
                try:
                    orders = orders.order_by(*ordering)
                except:
                    return Response({'error': 'Invalid ordering field'}, status.HTTP_400_BAD_REQUEST)
            paginator = Paginator(items, per_page=per_page)
            try:
                items = paginator.page(page)
            except EmptyPage:
                items = []
            serialized_item = MenuItemSerializer(items, many=True, context={'request': request})
            return Response(serialized_item.data, status.HTTP_200_OK)
    else:
        if request.user.groups.filter(name='Manager').exists(): 
            serialized_item = MenuItemSerializer(data=request.data, context={'request': request})
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status.HTTP_201_CREATED)          
        else:
            return Response({'error': 'You are not allowed to perform this action'}, status.HTTP_401_UNAUTHORIZED)
        

@api_view(['GET','PUT','DELETE','PATCH'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def single_item(request,id):
    if request.method == 'GET':
        item = get_object_or_404(MenuItem,pk=id)
        serialized_item = MenuItemSerializer(item)
        return Response(serialized_item.data, status.HTTP_200_OK)
    else:
        if request.user.groups.filter(name='Manager').exists(): 
            item = get_object_or_404(MenuItem,pk=id)
            if request.method == 'PUT':
                serialized_item = MenuItemSerializer(item, data=request.data, context={'request': request})
                serialized_item.is_valid(raise_exception=True)
                serialized_item.save()
                return Response(serialized_item.data)
            elif request.method == 'PATCH':
                serialized_item = MenuItemSerializer(item, data=request.data, context={'request': request}, partial=True)
                serialized_item.is_valid(raise_exception=True)
                serialized_item.save()
                return Response(serialized_item.data)
            else:
                item.delete()
                return Response({'message': 'Item deleted successfully'})
        else:
            return Response({'error': 'You are not allowed to perform this action'}, status.HTTP_401_UNAUTHORIZED)
        
@api_view(['GET','POST'])
@permission_classes([IsManager | IsAdminUser])
@throttle_classes([ManagerRateThrottle])
def managers(request):
    if request.method == 'GET':
        managers = User.objects.filter(groups__name='Manager')
        serialized_managers = UserSerializer(managers, many=True)
        return Response(serialized_managers.data, status.HTTP_200_OK)
    else:
        username = request.data['username']
        if username:
            user = get_object_or_404(User,username=username)
            managers = Group.objects.get(name='Manager')
            managers.user_set.add(user)
            return Response({'message': 'User added to managers group'}, status.HTTP_201_CREATED)
        return Response({'error': 'Username is required'}, status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsManager | IsAdminUser])
@throttle_classes([ManagerRateThrottle])
def remove_manager(request, id):
    user = get_object_or_404(User,pk=id)
    managers = Group.objects.get(name='Manager')
    managers.user_set.remove(user)
    return Response({'message': 'User removed from managers group'}, status.HTTP_200_OK)

@api_view(['GET','POST'])
@permission_classes([IsManager | IsAdminUser])
@throttle_classes([ManagerRateThrottle])
def delivery_crew(request):
    if request.method == 'GET':
        delivery_crew = User.objects.filter(groups__name='Delivery Crew')
        serialized_delivery_crew = UserSerializer(delivery_crew, many=True)
        return Response(serialized_delivery_crew.data, status.HTTP_200_OK)
    else:
        username = request.data['username']
        if username:
            user = get_object_or_404(User,username=username)
            delivery_crew = Group.objects.get(name='Delivery Crew')
            delivery_crew.user_set.add(user)
            return Response({'message': 'User added to Delivery Crew group'}, status.HTTP_201_CREATED)
        return Response({'error': 'Username is required'}, status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsManager | IsAdminUser])
@throttle_classes([ManagerRateThrottle])
def remove_delivery_crew(request, id):
    user = get_object_or_404(User,pk=id)
    delivery_crew = Group.objects.get(name='Delivery Crew')
    delivery_crew.user_set.remove(user)
    return Response({'message': 'User removed from Delivery Crew group'}, status.HTTP_200_OK)

@api_view(['GET','POST','DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def cart(request):    
    if request.method == 'GET':
        carts = Cart.objects.filter(user=request.user)
        serialized_carts = CartSerializer(carts, many=True)
        return Response(serialized_carts.data, status.HTTP_200_OK)
    
    elif request.method == 'POST':
        menu_item = get_object_or_404(MenuItem,pk=request.data['menuitem_id'])
        data = {
            'user_id': request.user.id,
            'menuitem_id': request.data['menuitem_id'],
            'quantity': request.data['quantity'],
            'unit_price': menu_item.price,
            'price': round(menu_item.price * int(request.data['quantity']),2)
        }
        serialized_carts = CartSerializer(data=data)
        serialized_carts.is_valid(raise_exception=True)
        serialized_carts.save()
        return Response(serialized_carts.data, status.HTTP_201_CREATED)
    
    elif request.method == 'DELETE':
        carts = Cart.objects.filter(user=request.user)
        for cart in carts:
            cart.delete()
        return Response({'message': 'All items removed from cart'}, status.HTTP_200_OK)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def orders(request):
    if request.method == 'GET':
        if request.user.groups.filter(name='Manager'):
            orders = Order.objects.prefetch_related('order_items').all()
        elif request.user.groups.filter(name='Delivery Crew'):
            orders = Order.objects.prefetch_related('order_items').filter(delivery_crew=request.user)
        else:
            orders = Order.objects.prefetch_related('order_items').filter(user=request.user)
        per_page = request.query_params.get('perpage',default=4)
        page = request.query_params.get('page',default=1)
        ordering = request.query_params.get('ordering')
        statuss = request.query_params.get('status')
        delivery_crew = request.query_params.get('delivery_crew')
        if statuss:
            orders = orders.filter(status=statuss)
        if delivery_crew:
            orders = orders.filter(delivery_crew__username__icontains=delivery_crew)
        if ordering:
            ordering = ordering.split(',')
            try:
                orders = orders.order_by(*ordering)
            except:
                return Response({'error': 'Invalid ordering field'}, status.HTTP_400_BAD_REQUEST)
        paginator = Paginator(orders, per_page=per_page)
        try:
            orders = paginator.page(page)
        except EmptyPage:
            orders = []
        serialized_orders = OrderSerializer(orders, many=True)
        return Response(serialized_orders.data, status.HTTP_200_OK)
    else:
        carts = Cart.objects.filter(user=request.user)
        if not carts.exists():
            return Response({'error': 'Cart is empty'}, status.HTTP_400_BAD_REQUEST)
        total = sum([cart_item.price for cart_item in carts])
        order = Order.objects.create(user=request.user, status=False, total = total, date = date.today())
        order.save()
        for cart_item in carts:
            order_item = OrderItem.objects.create(order=order, menuitem=cart_item.menuitem, quantity=cart_item.quantity, unit_price=cart_item.unit_price, price=cart_item.price)
            order_item.save()
            cart_item.delete()
        return Response({'message': 'Order placed successfully'}, status.HTTP_201_CREATED)
    
@api_view(['GET','PUT','DELETE','PATCH'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def single_order(request,id):
    order = get_object_or_404(Order,pk=id)
    if request.method == 'GET':
        if request.user != order.user and not request.user.groups.filter(name='Manager').exists():
            return Response({'error': 'You are not allowed to perform this action'}, status.HTTP_401_UNAUTHORIZED)
        serialized_order = OrderSerializer(order)
        return Response(serialized_order.data, status.HTTP_200_OK)
    elif request.method == 'PUT':
        if request.user.groups.filter(name='Manager').exists():
            if 'crew_id' in request.data:
                delivery_crew = get_object_or_404(User,pk=request.data['crew_id'])
                if not delivery_crew.groups.filter(name='Delivery Crew').exists():
                    return Response({'error': 'User is not in Delivery Crew group'}, status.HTTP_400_BAD_REQUEST)
                order.delivery_crew = delivery_crew
            if 'status' in request.data:
                order.status = request.data['status']
            order.save()
            return Response({'message': 'Order status updated successfully'}, status.HTTP_200_OK)
        return Response({'error': 'You are not allowed to perform this action'}, status.HTTP_401_UNAUTHORIZED)
    elif request.method == 'DELETE':
        if request.user.groups.filter(name='Manager').exists():
            order.delete()
            return Response({'message': 'Order deleted successfully'}, status.HTTP_200_OK)
        return Response({'error': 'You are not allowed to perform this action'}, status.HTTP_401_UNAUTHORIZED)
    elif request.method == 'PATCH':
        if request.user.groups.filter(name='Delivery Crew').exists() or request.user.groups.filter(name='Manager').exists():
            order.status = request.data['status']
            order.save()
            return Response({'message': 'Status changed successfully successfully'}, status.HTTP_200_OK)
        return Response({'error': 'You are not allowed to perform this action'}, status.HTTP_401_UNAUTHORIZED)


#endregion
        
#region Class-based views
        
class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price','inventory']
    filterset_fields = ['price','inventory']
    search_fields = ['category__title','title']

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method != 'GET':
            permission_classes = [IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]
    
class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method != 'GET':
            permission_classes = [IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]
    
class ManagersView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = UserSerializer
    permission_classes = [IsManager | IsAdminUser]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User,username=username)
            managers = Group.objects.get(name='Manager')
            managers.user_set.add(user)
            return Response({'message': 'User added to managers group'}, status.HTTP_201_CREATED)
        return Response({'error': 'Username is required'}, status.HTTP_400_BAD_REQUEST)
class RemoveManagerView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsManager | IsAdminUser]

    def delete(self, request, *args, **kwargs):
        user = get_object_or_404(User,pk=kwargs['pk'])
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)
        return Response({'message': 'User removed from managers group'}, status.HTTP_200_OK)
    
class DeliveryCrewView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name = 'Delivery Crew')
    serializer_class = UserSerializer
    permission_classes = [IsManager | IsAdminUser]

    def post(self, request,*args,**kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User,username=username)
            delivery_crew = Group.objects.get(name='Delivery Crew')
            delivery_crew.user_set.add(user)
            return Response({'message': 'User added to Delivery Crew group'}, status.HTTP_201_CREATED)
        return Response({'error': 'Username is required'}, status.HTTP_400_BAD_REQUEST)
    
class RemoveDeliveryCrewView(generics.DestroyAPIView):
    queryset = User.objects.filter(groups__name='Delivery Crew')
    serializer_class = UserSerializer

    def delete(self, request, *args, **kwargs):
        user = get_object_or_404(User,pk=kwargs['pk'])
        delivery_crew = Group.objects.get(name='Delivery Crew')
        delivery_crew.user_set.remove(user)
        return Response({'message': 'User removed from Delivery Crew group'}, status.HTTP_200_OK)
    
class CartView(generics.ListCreateAPIView,generics.DestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def post(self, request, *args, **kwargs):
        menu_item = get_object_or_404(MenuItem,pk=request.data['menuitem_id'])
        data = {
            'user_id': request.user.id,
            'menuitem_id': request.data['menuitem_id'],
            'quantity': request.data['quantity'],
            'unit_price': menu_item.price,
            'price': round(menu_item.price * int(request.data['quantity']),2)
        }
        serialized_carts = CartSerializer(data=data)
        serialized_carts.is_valid(raise_exception=True)
        serialized_carts.save()
        return Response(serialized_carts.data, status.HTTP_201_CREATED)
    
    def delete(self, request, *args, **kwargs):
        Cart.objects.filter(user=self.request.user).delete()
        return Response({'message': 'All items removed from cart'}, status.HTTP_200_OK)
    
class OrdersView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif self.request.user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=self.request.user)
        return Order.objects.filter(user=self.request.user)
    
    def post(self, request, *args, **kwargs):
        carts = Cart.objects.filter(user=request.user)
        if not carts.exists():
            return Response({'error': 'Cart is empty'}, status.HTTP_400_BAD_REQUEST)
        total = sum([cart_item.price for cart_item in carts])
        order = Order.objects.create(user=request.user, status=False, total = total, date = date.today())
        order.save()
        for cart_item in carts:
            order_item = OrderItem.objects.create(order=order, menuitem=cart_item.menuitem, quantity=cart_item.quantity, unit_price=cart_item.unit_price, price=cart_item.price)
            order_item.save()
            cart_item.delete()
        return Response({'message': 'Order placed successfully'}, status.HTTP_201_CREATED)
    
class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        order = get_object_or_404(Order,pk=kwargs['pk'])
        if self.request.user!=order.user and not self.request.user.groups.filter(name='Manager'):
            return Response({'error': 'You are not allowed to perform this action'}, status.HTTP_401_UNAUTHORIZED)
        return super().get(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        order = get_object_or_404(Order,pk=kwargs['pk'])
        if request.user.groups.filter(name='Manager').exists():
            if 'crew_id' in request.data:
                delivery_crew = get_object_or_404(User,pk=request.data['crew_id'])
                if not delivery_crew.groups.filter(name='Delivery Crew').exists():
                    return Response({'error': 'User is not in Delivery Crew group'}, status.HTTP_400_BAD_REQUEST)
                order.delivery_crew = delivery_crew
            if 'status' in request.data:
                order.status = request.data['status']
            order.save()
            return Response({'message': 'Order updated successfully'}, status.HTTP_200_OK)
        return Response({'error': 'You are not allowed to perform this action'}, status.HTTP_401_UNAUTHORIZED)
    
    def patch(self, request, *args, **kwargs):
        order = get_object_or_404(Order,pk=kwargs['pk'])
        if request.user.groups.filter(name='Delivery Crew').exists() or request.user.groups.filter(name='Manager').exists():
            order.status = request.data['status']
            order.save()
            return Response({'message': 'Status changed successfully successfully'}, status.HTTP_200_OK)
        return Response({'error': 'You are not allowed to perform this action'}, status.HTTP_401_UNAUTHORIZED)
#endregion
