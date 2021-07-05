from django.contrib import admin
from .models import Product, Variation, ReviewRating, ProductGallery
import admin_thumbnails

# Register your models here.
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1 # To add more images




class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category','created_date', 'modified_date', 'is_available')
    prepopulated_fields = {'slug' : ('product_name',)}
    inlines = [ProductGalleryInline]


class VariationAdmin(admin.ModelAdmin):
    list_display  = ('product', 'variation_cat', 'variation_value','variation_price', 'created_date', 'is_active')
    list_editable = ('is_active',)
    list_filter   = ('product', 'variation_cat', 'variation_value')
    

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)