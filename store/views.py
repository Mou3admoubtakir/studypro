from django.shortcuts import redirect, render
from django.http import JsonResponse
from store.models import Customer, Order, OrderItem, Product, ShippingAddress
from django.core.paginator import Paginator
import json
import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .forms import CreateUserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .utils import cookieCart, cardData
# Create your views here.


def store(request):
    data = cardData(request)
    cartItems = data['cartItems']
    user = request.user
    print(user)
    products = Product.objects.all()[:6]
    context = {'products': products,
               'cartItems': cartItems, }
    return render(request, 'store/store.html', context)

# else : cookie stuff and for if is authenticated user


def cart(request):
    data = cardData(request)

    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cardData(request)

    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


# in here we process add to cart and add order items total etccc direction cart.html and cart.js
def updateItem(request):
    data = json.loads(request.body)
    user = request.user
    print(user)
    productId = data['productId']
    action = data['action']
    print("ProductId :", productId)
    print("action", action)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Items was added ...', safe=False)


# Here we proccess the shipping (details in checkout.html)
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    print(data)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

    else:
        print("user is not logged in !!")
        print('COOKIES:', request.COOKIES)
        name = data['form']['name']
        email = data['form']['email']

        cookieData = cookieCart(request)
        items = cookieData['items']

        customer, created = Customer.objects.get_or_create(email=email)
        customer.name = name
        customer.save()

        order = Order.objects.create(customer=customer, complete=False)
        for item in items:
            product = Product.objects.get(id=item['product']['id'])
            orderItem = OrderItem.objects.create(
                product=product, order=order, quantity=item['quantity'])
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_card_total:
        order.complete = True
    order.save()
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer, order=order, address=data['shipping'][
                'address'], city=data['shipping']['city'], state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted ... ', safe=False)


# Here the second part of registration and logged in :P
def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")

    context = {'form': form}
    return render(request, 'store/register.html', context)


def loginPage(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.info(request, 'username or password is incorrect')
    context = {}
    return render(request, 'store/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect("login")


def dashboard(request):
    if request.user.is_authenticated:
        orders = Order.objects.all()
        total_revenue = 0
        for order in orders:
            total_revenue += float(order.get_card_total)
        context = {'orders': orders, 'total_revenue': total_revenue,
                   'total_orders': len(orders)}
        return render(request, 'store/dashboard.html', context)
    else:
        return redirect("login")


def all_products(request):
    products = Product.objects.all()
    item_name = request.GET.get("item_name")
    if item_name != "" and item_name is not None:
        products = products.filter(name__icontains=item_name)
    paginator = Paginator(products, 6)
    page = request.GET.get("page")
    products = paginator.get_page(page)
    # take data
    data = cardData(request)
    cartItems = data['cartItems']
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/all_products.html', context)


def all_products_admin(request):
    if request.user.is_authenticated:
        products = Product.objects.all()
        item_name = request.GET.get("item_name")
        if item_name != "" and item_name is not None:
            products = products.filter(name__icontains=item_name)
        paginator = Paginator(products, 6)
        page = request.GET.get("page")
        products = paginator.get_page(page)
        if request.method == "POST":
            image = request.POST['image']
            price = request.POST['price']
            name = request.POST['name']
            new_product = Product(image=image, price=price, name=name)
            new_product.save()
            messages.success(
                request, f"Product added succesfully by {request.user.username}!")
            products = Product.objects.all()
    else:
        products = {}
    context = {'products': products}
    return render(request, 'store/all_products_admin.html', context)


def delete_product(request, id=None):
    Product.objects.get(id=id).delete()
    return redirect("all_products_admin")


def view_product(request, id):
    if request.user.is_authenticated:
        product = Product.objects.get(id=id)
    else:
        product = ''
    context = {'product': product}
    return render(request, 'store/view_product.html', context)


def update_product(request, id):
    if request.method == "POST":
        image = request.POST.get("image")
        name = request.POST.get("name")
        price = request.POST.get("price")
        Product.objects.filter(id=id).update(
            image=image, name=name, price=price)
        return redirect("all_products_admin")
    product = Product.objects.get(id=id)
    context = {'product': product}
    return render(request, 'store/update_product.html', context)
