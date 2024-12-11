from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_, name='logout'),
    path('profile/', views.profile, name='profile'),

    # Password reset and change
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('password_reset_success', views.password_reset_success, name='password_reset_success'),
    path('password_change/<uidb64>/<token>/', views.change_password, name='password_change'),

    # Location and services pages
    path('location/', views.location, name='location'),
    path('suppliers/', views.suppliers, name='suppliers'),
    path('about_us/', views.about_us, name='about_us'),
    path('contact/', views.contact, name='contact'),

    # Services routes
    path('photographers/', views.photographers, name='photographers'),
    path('decorators/', views.decorators, name='decorators'),
    path('menu_bar/', views.menu_bar, name='menu_bar'),
    path('choreographers/', views.choreographers, name='choreographers'),
    path('designers/', views.designers, name='designers'),
    path('venue_planners/', views.venue_planners, name='venue_planners'),
    path('makeup_artists/', views.makeup_artists, name='makeup_artists'),

    # After order, cart, and bookings
    path('after_order/', views.after_order, name='after_order'),
    path('my_orders/', views.my_orders, name='orders'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('blocked-dates/', views.get_blocked_dates, name='blocked_dates'),

    # Manager pages
    path('manager/', views.manager_page, name='manager'),
    path('manager/edit/<int:pk>/', views.edit_booking, name='edit_booking'),
    path('manager/delete/<int:pk>/', views.delete_booking, name='delete_booking'),
    path('update_status/', views.update_status, name='update_status'),

]

# Static files (CSS, JavaScript, images) serving in development
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)