from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.password_validation import validate_password
# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)],help_text="Current stock quantity",blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(blank=True,null=True)

    def __str__(self):
        return self.product_name
    
    def update_quantity(self, quantity_change):
        """
        Method to update product quantity
        Can be used for sales, restocking, etc.
        """
        self.stock_quantity += quantity_change
        self.save()
        
        
    def quantity_left(self,ramaining_quantity):
        """
        Method to calculate product quantity left
        """    
        self.remaining_quantity = self.stock_quantity - Sale.product_quantity
        self.save>()
    
class Category(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)    

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Sale(models.Model):
    #user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sales')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,null=True, related_name='sales') 
    date = models.DateTimeField(auto_now=True) 
    quantity_sold = models.PositiveIntegerField() 
    unit_price = models.DecimalField(max_digits=10,decimal_places=2, validators=[MinValueValidator(0)])
    total_sale = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return f"{self.product.product_name} - {self.quantity_sold} units"
    
    def save(self, *args, **kwargs):
        self.total_sale = self.quantity_sold * self.unit_price
        super().save(*args, **kwargs)