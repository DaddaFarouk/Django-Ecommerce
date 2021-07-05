from django.contrib import admin
from .models import Product, Variation, ReviewRating

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category','created_date', 'modified_date', 'is_available')
    prepopulated_fields = {'slug' : ('product_name',)}


class VariationAdmin(admin.ModelAdmin):
    list_display  = ('product', 'variation_cat', 'variation_value','variation_price', 'created_date', 'is_active')
    list_editable = ('is_active',)
    list_filter   = ('product', 'variation_cat', 'variation_value')
    

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)