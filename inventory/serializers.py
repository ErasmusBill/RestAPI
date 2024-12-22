from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Product, Category, Sale
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=155)
    last_name = serializers.CharField(max_length=255)
    
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",  #
            "last_name",
            "username",
            "email",
            "password",
        ]
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data,password=password)
        return user
        
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    remaining_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id',
            'product_name',
            'description',
            'stock_quantity',
            'price',
            'date',
            'image',
            'remaining_stock'
        ]
        read_only_fields = ['date']

    def get_remaining_stock(self, obj):
        """Calculate remaining stock after all sales"""
        total_sales = sum(sale.quantity_sold for sale in obj.sale_set.all())
        return obj.stock_quantity - total_sales

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero")
        return value


class CategorySerializer(serializers.ModelSerializer):
    # Using nested serializer for product details
    product = ProductSerializer()
    sales_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'product', 'sales_count']

    def get_sales_count(self, obj):
        return obj.sales.count()

    def create(self, validated_data):
        product_data = validated_data.pop('product')
        # First create or get the product
        product = Product.objects.create(**product_data)
        # Then create the category
        category = Category.objects.create(product=product, **validated_data)
        return category


class SaleSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id',
            'product',
            'product_name',
            'category',
            'category_name',
            'date',
            'quantity_sold',
            'unit_price',
            'total_sale'
        ]
        read_only_fields = ['date', 'total_sale']

    def validate(self, data):
        """
        Check that the quantity sold doesn't exceed available stock
        and that the unit price matches the product price
        """
        product = data['product']
        quantity_sold = data['quantity_sold']
        unit_price = data['unit_price']

        # Validate quantity
        if quantity_sold > product.stock_quantity:
            raise serializers.ValidationError({
                "quantity_sold": f"Cannot sell {quantity_sold} units. Only {product.stock_quantity} available."
            })

        # Validate price matches product price (optional, remove if prices can differ)
        if unit_price != product.price:
            raise serializers.ValidationError({
                "unit_price": f"Unit price must match product price of {product.price}"
            })

        # Validate category matches product
        if data['category'].product != product:
            raise serializers.ValidationError({
                "category": "Category must match the product's category"
            })

        return data

    def create(self, validated_data):
        # Calculate total sale
        validated_data['total_sale'] = validated_data['quantity_sold'] * validated_data['unit_price']
        
        # Create the sale
        sale = Sale.objects.create(**validated_data)
        
        # Update product quantity
        product = validated_data['product']
        product.update_quantity(-validated_data['quantity_sold'])
        
        return sale



class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        
        # Validate password strength
        validate_password(data['new_password'])
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user 