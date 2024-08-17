from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User, Group
from decimal import Decimal
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    price_after_tax = serializers.SerializerMethodField(method_name='CalculateTax')    
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'price_after_tax', 'featured', 'category', 'category_id']
        validators = [
            UniqueTogetherValidator(
                queryset=MenuItem.objects.all(),
                fields=['title', 'price', 'category_id']
            ),
        ]

    def validate_price(self, value):
        if value < 2:
            raise serializers.ValidationError('Price must be greater than 2')
        return value

    def CalculateTax(self, product : MenuItem):
        return round(product.price * Decimal(1.12),2)
    
class GroupSerializer(serializers.ModelSerializer):  
        class Meta:
            model = Group
            fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class SimpleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price']
    def validate_price(self, value):
        if value < 2:
            raise serializers.ValidationError('Price must be greater than 2')
        return value

class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    menuitem = SimpleItemSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price', 'menuitem_id', 'user_id']
        validators = [UniqueTogetherValidator(
            queryset=Cart.objects.all(),
            fields=['user_id', 'menuitem_id']
        )]
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Quantity must be greater than 0')
        return value
    def validate_price(self, value):
        if value < 2:
            raise serializers.ValidationError('Price must be greater than 2')
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = SimpleItemSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity', 'price']
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Quantity must be greater than 0')
        return value
    def validate_price(self, value):
        if value < 2:
            raise serializers.ValidationError('Price must be greater than 2')
        return value

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    delivery_crew = UserSerializer(read_only=True)
    order_items = OrderItemSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField(method_name='get_status')
    class Meta:
        model = Order
        fields = ['id', 'user', 'order_items', 'delivery_crew', 'status', 'total', 'date']

    def get_status(self, order : Order):
        return 'Delivered' if order.status else 'Pending'
    
    def validate_total(self,value):
        if value < 2:
            raise serializers.ValidationError('Total must be greater than 2')
        return value