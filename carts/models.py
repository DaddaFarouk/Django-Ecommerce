from django.db import models
from store.models import Product, Variation
from accounts.models import Account

# Create your models here.

class Cart(models.Model):
    cart_id     = models.CharField(max_length=250, blank=True)
    date_added  = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product     = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations  = models.ManyToManyField(Variation, blank=True) # because each product can have different variations
    cart        = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity    = models.IntegerField()
    is_active   = models.BooleanField(default=True)

    
    def sub_total(self):
        total=0
        for item in self.variations.all():
            total += item.variation_price

        if total != 0:
            return total * self.quantity
        else:
            return self.product.price * self.quantity
        
    def item_price(self):
        total=0
        for item in self.variations.all():
            total += item.variation_price

        if total != 0:
            return total
        else:
            return self.product.price


    #def sub_total(self):
        #return self.product.price * self.quantity

    def __unicode__(self):
        return self.product