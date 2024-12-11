import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import RegisterForm, LoginForm, CustomSetPasswordForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from decimal import Decimal
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from django.core.mail import send_mail
from .models import Page, Cart
from .models import Order
from .models import Location, Booking
from django.shortcuts import get_object_or_404
from .forms import OrderForm


# Create your views here.
def signin(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('manager')
                return redirect('home')
            else:
                form.add_error(None, "Invalid email or password")
    else:
        form = LoginForm()

    return render(request, 'core/signin.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if 'happyholiday' in user.email:
                user.is_staff = True
            user.save()

            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                if 'happyholiday' in user.email:
                    return redirect('manager')
                return redirect('home')
        else:
            print('Form errors:', form.errors)
    else:
        form = RegisterForm()
    return render(request, 'core/signup.html', {'form': form})


def logout_(request):
    logout(request)
    return redirect('home')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        associated_user = User.objects.filter(email=email).first()
        print(f"Email entered: {email}")
        print(f"Associated user found: {associated_user}")

        if associated_user:
            subject = 'Password Reset Requested'
            email_template_name = 'core/password_reset_email.html'
            context = {
                'email': associated_user.email,
                'domain': get_current_site(request).domain,
                'site_name': "Happy Holiday",
                'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                'token': default_token_generator.make_token(associated_user),
                'protocol': 'https' if request.is_secure() else 'http',
            }

            email_content = render_to_string(email_template_name, context)
            send_mail(subject, email_content, '200107017@stu.sdu.edu.kz', [associated_user.email], fail_silently=False)
            messages.success(request, 'A reset code has been sent to your email address.')
        else:
            messages.error(request, 'The specified email is not registered.')

    return render(request, 'core/forgot-password.html', {})


def password_reset_success(request):
    return render(request, 'core/password_reset_success.html', {})


def change_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        print(uid, user)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        print(urlsafe_base64_encode(uidb64).decode())
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)

            if form.is_valid():
                form.save()
                return redirect('home')
        else:
            form = CustomSetPasswordForm(user)
        return render(request, 'core/password_reset.html', {'form': form, 'correct': True})
    else:
        return render(request, 'core/password_reset.html', {'correct': False})


def home(request):
    user_id = request.user.id

    return render(request, 'core/home.html', {'id': user_id})


def profile(request):
    user_id = request.user.id

    return render(request, 'core/profile.html', {'id': user_id})


def my_orders_view(request):
    carts = Cart.objects.filter(user=request.user)
    if not request.user.is_authenticated:
        return redirect('login')  # Перенаправить на страницу входа, если пользователь не авторизован

    orders = Order.objects.filter(user=request.user)  # Получаем заказы текущего пользователя
    return render(request, 'my_orders.html', {'orders': orders})


def manager_page(request):
    return render(request, 'core/manager_home.html', {})


def location(request):
    # Get query parameters from the request
    location = request.GET.get('location', '')
    date = request.GET.get('date', '')
    guests = request.GET.get('guests', '')

    # Start with all locations
    locations = Location.objects.all()

    # Filter by location type if provided
    if location:
        locations = locations.filter(location_type=location)

    # Filter by exact guest capacity (matching choices)
    if guests and guests in dict(Location.CAPACITY_CHOICES):
        locations = locations.filter(number_of_guests=guests)

    # Exclude locations already booked on the specified date
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            locations = locations.exclude(bookings__booking_date=date_obj)
        except ValueError:
            return render(request, 'core/locations.html', {
                'locations': [],
                'error': 'Invalid date format. Use YYYY-MM-DD.',
                'filters': {'location': location, 'date': date, 'guests': guests}
            })

    # Get the user's cart items
    carts = Cart.objects.filter(user=request.user) if request.user.is_authenticated else []
    locations_in_cart = set(carts.values_list('location_id', flat=True)) if carts else set()

    # Render the results
    return render(request, 'core/locations.html', {
        'SW': locations.filter(location_type='SV'),
        'MW': locations.filter(location_type='MV'),
        'CC': locations.filter(location_type='CC'),
        'cart_num': len(carts),
        'locations_in_cart': locations_in_cart,  # Locations already in the cart
        'filters': {'location': location, 'date': date, 'guests': guests}  # Pass filters to the template
    })




def suppliers(request):
    context = {}
    if request.user.is_authenticated:
        context['id'] = request.user.id  # Pass user ID to the context
    return render(request, 'core/suppliers.html', context)


def about_us(request):
    context = {}
    if request.user.is_authenticated:
        context['id'] = request.user.id  # Pass user ID to the context
    return render(request, 'core/about_us.html', context)


def contact(request):
    return render(request, 'core/contact.html')


# Suppliers
def photographers(request):
    context = {}
    if request.user.is_authenticated:
        context['id'] = request.user.id  # Pass the user's ID to the context
    return render(request, 'core/suppliers/photographers.html', context)


def decorators(request):
    context = {}
    if request.user.is_authenticated:
        context['id'] = request.user.id  # Pass the user's ID to the context
    return render(request, 'core/suppliers/decorators.html', context)


def menu_bar(request):
    context = {}
    if request.user.is_authenticated:
        context['id'] = request.user.id  # Pass the user's ID to the context
    return render(request, 'core/suppliers/menu_bar.html', context)


def choreographers(request):
    context = {}
    if request.user.is_authenticated:
        context['id'] = request.user.id  # Pass the user's ID to the context
    return render(request, 'core/suppliers/choreographers.html', context)


def designers(request):
    context = {}
    if request.user.is_authenticated:
        context['id'] = request.user.id  # Pass the user's ID to the context
    return render(request, 'core/suppliers/designers.html', context)


def venue_planners(request):
    context = {}
    if request.user.is_authenticated:
        context['id'] = request.user.id  # Pass the user's ID to the context
    return render(request, 'core/suppliers/venue_planners.html', context)


def makeup_artists(request):
    context = {}
    if request.user.is_authenticated:
        context['id'] = request.user.id  # Pass the user's ID to the context
    return render(request, 'core/suppliers/makeup_artists.html', context)


@login_required
@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            location_name = data.get("name")
            location = Location.objects.get(name=location_name)
            user = request.user
            Cart.objects.create(location=location, user=user)

            return JsonResponse({"message": "Item added to cart successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required()
def cart(request):
    cart = Cart.objects.filter(user=request.user.id)

    price = 0
    for c in cart:
        price += c.location.base_price
    context = {
        'cart': cart,
        'price': price,
    }

    return render(request, 'core/cart.html', context)


def after_order(request):
    if request.method == 'POST':
        try:
            # Get the JSON data from the frontend
            data = json.loads(request.body)
            print(data)  # Логируем полученные данные

            total_price = Decimal(data['totalPrice'].split(' ')[0])
            location = Location.objects.get(pk=data['locationId'])

            Order.objects.create(
                user=request.user,
                total_price=total_price
            )

            # Clear the cart after order creation
            Cart.objects.filter(user=request.user, location=location).delete()

            return JsonResponse({'message': 'Order created successfully'})
        except Exception as e:
            print(f"Error in after_order: {e}")  # Логируем ошибку
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def my_orders(request):
    order = Order.objects.filter(user=request.user.id)
    print(order)

    return render(request, 'core/my_orders.html', {'orders': order})


def get_blocked_dates(request):
    blocked_dates = Booking.objects.values_list('booking_date', flat=True)
    return JsonResponse(list(blocked_dates), safe=False)


def delete_order(request, order_id):
    Order.objects.get(pk=order_id).delete()
    return redirect('orders')


def manager_page(request):
    bookings = Booking.objects.all()
    orders = Order.objects.all()
    bookings = Booking.objects.all()
    return render(request, 'core/manager_home.html', {'bookings': bookings})


def edit_booking(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('manager')
    else:
        form = OrderForm(instance=order)
    return render(request, 'core/booking_form.html', {'form': form, 'title': 'Edit Booking'})


def delete_booking(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('manager')
    return render(request, 'core/confirm_delete.html', {'order': order})


@csrf_exempt
def update_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')

        # Найдем заказ и обновим его статус
        try:
            order = Order.objects.get(id=order_id)
            order.status = new_status
            order.save()
            return JsonResponse({'status': 'success'})
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'})

