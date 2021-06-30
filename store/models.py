from django.db import models
from category.models import Category
from django.urls import reverse

# Create your models here.

class Product(models.Model):
    product_name    = models.CharField(max_length=200, unique=True)
    slug            = models.SlugField(max_length=200, unique=True)
    description     = models.TextField(max_length=500, blank=True)
    price           = models.FloatField()
    images          = models.ImageField(upload_to='photos/products')
    stock           = models.IntegerField()
    is_available    = models.BooleanField(default=True)
    category        = models.ForeignKey(Category, on_delete=models.CASCADE) 
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['product_name',]

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

class VariationManager(models.Manager):
    def editions(self):
        return super(VariationManager, self).filter(variation_cat='edition', is_active=True)

    def platforms(self):
        return super(VariationManager, self).filter(variation_cat='platform', is_active=True)


variation_cat_choice = (
    ('edition','edition'),
    ('platform','platform'),
)

class Variation(models.Model):
    product         = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_cat   = models.CharField(max_length=100, choices=variation_cat_choice)
    variation_value = models.CharField(max_length=100)
    variation_price = models.FloatField(default=0)
    is_active       = models.BooleanField(default=True)
    created_date    = models.DateTimeField(auto_now=True)

    objects = VariationManager() # use the fonctions

    def __str__(self):
        return self.variation_value