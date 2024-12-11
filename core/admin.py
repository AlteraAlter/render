from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_type', 'number_of_guests', 'base_price')
    list_filter = ('location_type', 'number_of_guests')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('location', 'user', 'rating', 'comment')
    list_filter = ('rating', 'location')
    search_fields = ('location__name', 'user__username', 'comment')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('location', 'user', 'booking_date')
    list_filter = ('booking_date', 'location')
    search_fields = ('location__name', 'user__username')
    ordering = ('booking_date',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('location', 'user')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'total_price', 'created_at')
