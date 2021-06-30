from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, Variation
from .models import Cart, CartItem

# Create your views here.

def _cart_id(request): # get the user's session id
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart



def add_cart(request, product_id):  # update or create a cart if not exists
    product = Product.objects.get(id=product_id) # get the product
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:   # loop in the keys
            key = item # store the key
            value = request.POST[key] # store the key value
            try:
                variation = Variation.objects.get(product=product, variation_cat__iexact=key, variation_value__iexact=value) #get the variation for this product
                product_variation.append(variation) # store the variation in the list
            except:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the session id
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save() #insert Cart to database

    cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

    if cart_item_exists: 
        cart_item  = CartItem.objects.filter(product=product, cart=cart)
        # existing_variations from database
        # current variations from product_variation
        # item_id from database
        existing_variations = []
        id = []
        for item in cart_item:
            ex_variation = item.variations.all() # get each variations
            existing_variations.append(list(ex_variation)) # Because the ex_variation is a QuerySet
            id.append(item.id)

        if product_variation in existing_variations: # if the product variation already exists in the cart
            # increase the Item quantity
            index = existing_variations.index(product_variation)  # get the product variations index from the list
            item_id = id[index] 
            item = CartItem.objects.get(product=product, id=item_id) # select the existing CartItem from the cart
            item.quantity += 1
            item.save()
        else:
            # create new Item
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0: # If there are any product variations
                item.variations.clear() 
                item.variations.add(*product_variation) # add productvariation to the CartItem
  
            item.save()  

    else: # if the CartItem doesn't exist
        cart_item = CartItem.objects.create(
            product  = product,
            quantity = 1,
            cart = cart,
        ) 
        if len(product_variation) > 0: # If there are any product variations
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation) # add productvariation to the CartItem

        cart_item.save() 


    return redirect('cart')



def remove_cart(request, product_id, cart_item_id):
    cart      = Cart.objects.get(cart_id = _cart_id(request))
    product   = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    cart      = Cart.objects.get(cart_id=_cart_id(request))
    product   = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id= cart_item_id)
    cart_item.delete()
    return redirect('cart')





def cart(request, total=0, quantity=0, cart_items=None): 
    
    try:
        tax         = 0
        grand_total = 0
        cart        = Cart.objects.get(cart_id=_cart_id(request)) # get cart by id
        cart_items  = CartItem.objects.filter(cart=cart, is_active=True) # get cart items
        for cart_item in cart_items:
            total += (cart_item.item_price() * cart_item.quantity) # calculate total price
            quantity += cart_item.quantity
        tax = (20 * total)/100
        grand_total = total + tax

    except ObjectDoesNotExist: 
        pass # dont do anything

    context = {
        'total'      : total,
        'quantity'   : quantity,
        'cart_items' : cart_items,
        'tax'        : tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context) # send data to 'cart.html' template
