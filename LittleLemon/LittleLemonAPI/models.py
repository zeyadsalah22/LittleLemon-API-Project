from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=25,db_index=True)

    def __str__(self):
        return f'Category: {self.title}'

class MenuItem(models.Model):
    title = models.CharField(max_length=255,db_index=True)
    price = models.DecimalField(max_digits=6,decimal_places=2,db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category,on_delete=models.PROTECT)

    def __str__(self):
        return f'Item: {self.title} from {self.category.title} category'

class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem,on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6,decimal_places=2)
    price = models.DecimalField(max_digits=6,decimal_places=2)

    class Meta:
        unique_together = ('user','menuitem')

    def __str__(self):
        return f'{self.user.username} added Item: {self.menuitem.title} from {self.menuitem.category.title} category'

class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User,on_delete=models.SET_NULL,related_name='delivery_crew',null=True)
    status = models.BooleanField(db_index=True,default=False)
    total = models.DecimalField(max_digits=6,decimal_places=2)
    date = models.DateTimeField(db_index=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='order_items')
    menuitem = models.ForeignKey(MenuItem,on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6,decimal_places=2)
    price = models.DecimalField(max_digits=6,decimal_places=2)

    class Meta:
        unique_together = ('order','menuitem')