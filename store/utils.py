import json
from .models import *

# here what are we gonna do is paste the code bellow else int views.py
# And what this function actually does is render data for no authenticated user ;)


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    print(cart)
    items = []
    order = {'get_card_total': 0, 'get_card_items': 0, 'shipping': False}
    cartItems = order['get_card_items']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_card_total'] += total
            order['get_card_items'] += cart[i]['quantity']

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL,
                },
                'quantity': cart[i]['quantity'],
                'get_total': total,
            }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True
        except:
            pass
    return {'cartItems': cartItems, 'order': order, 'items': items}


# Here what are we gonna do is create a function that grab both method(for authenticated user and no auth.. )
# if and else in views remember!
def cardData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_card_items
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        cartItems = cookieData['cartItems']
        order = cookieData['order']
    return {'cartItems': cartItems, 'order': order, 'items': items}
