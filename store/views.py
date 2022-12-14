from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
import json
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.contrib import messages
import datetime
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.models import User


# Create your views here.


def home(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/home.html', context)


def product(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    categories = Book_category.objects.all()
    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems, 'category': categories}
    return render(request, 'store/product.html', context)


def about(request):
    return render(request, 'store/about.html')


def contact(request):
    return render(request, 'store/contact.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, f'Hi, {username} login successfull')
            if user.is_staff == True or user.is_superuser == True:
                return redirect('dashboard')
            return redirect('store')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'store/login.html')


def logout(request):
    auth.logout(request)
    return redirect('store')


def register(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password == password2:

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists!')
                return redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Email already exists!')
                    return redirect('register')
                else:
                    user = User.objects.create_user(first_name=firstname, last_name=lastname, email=email,
                                                    username=username, password=password)
                    auth.login(request, user)
                    messages.success(request, 'You are now logged in.')
                    return redirect('store')
                    user.save()
                    messages.success(request, 'You are registered successfully.')
                    return redirect('login')
        else:
            messages.error(request, 'Password do not match')
            return redirect('register')
    else:

        return render(request, 'store/register.html')


def book_register(request):
    categories = Book_category.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        price = request.POST.get('price')
        category = request.POST.get('category')
        cat = Book_category.objects.get(category_name=category)
        image = request.FILES.get('image')
        description = request.POST.get('description')
        Product.objects.create(name=title, price=price, category=cat, image=image, descriptions=description)
        return redirect('store')

    else:
        context = {
            'categories': categories,
        }

        return render(request, 'store/book_register.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action', action)
    print('productId', productId)

    customer = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == float(order.get_cart_total):
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(customer=customer,
                                           order=order,
                                           address=data['shipping']['address'],
                                           city=data['shipping']['city'],
                                           state=data['shipping']['state'],
                                           zipcode=data['shipping']['zipcode'],
                                           )
            print(order.shipping)
    else:
        print('User is not logged in...')
    return JsonResponse('Payment complete', safe=False)


def viewBook(request, pk):
    single_product = Product.objects.get(id=pk)


    context = {
        'product': single_product
    }
    return render(request, 'store/view_product.html', context)

def Dashboard(request):
    orderItems = OrderItem.objects.all()
    products = Product.objects.all().count()
    orders = Order.objects.all().count()
    users = User.objects.all().count()

    context = {
        'orderItems':orderItems,
        'users':users,
        'products':products,
        'orders':orders,
    }

    return render(request, 'store/dashboard.html', context)


@login_required
def profile(request):
    if request.method == 'POST':

        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():

            u_form.save()
            p_form.save()
            messages.success(request, f'Your Account have been updated')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {'u_form':u_form, 'p_form':p_form}
    return render(request, 'store/profile.html', context)
