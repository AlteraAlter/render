from datetime import date

from _decimal import Decimal
from django.db import models
from django.contrib.auth.models import User


class Page(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class Cart(models.Model):
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Location(models.Model):
    LOCATION_CHOICES = {
        ("SV", "Sea View"),
        ("MV", "Mountain View"),
        ("CC", "City Center")
    }

    CAPACITY_CHOICES = {
        ("2-6", "2 to 6"),
        ("7-15", "7 to 15"),
        ("16-30", "16 to 30"),
        ("30-50", "30 to 50")
    }

    name = models.CharField(max_length=255, null=True, blank=True)
    location_type = models.CharField(
        max_length=2,
        choices=LOCATION_CHOICES,
        null=True,
        blank=True
    )
    number_of_guests = models.CharField(
        max_length=10,
        choices=CAPACITY_CHOICES,
        null=True,
        blank=True
    )
    image = models.ImageField(upload_to='images', null=True, blank=True)
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('100.00')
    )
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Rating(models.Model):
    location = models.ForeignKey(Location, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_ratings', on_delete=models.CASCADE)  # Associate with User
    rating = models.DecimalField(max_digits=3, decimal_places=2)  # Rating out of 5
    comment = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('location', 'user')  # Ensure a user can rate a location only once

    def __str__(self):
        return f"Rating for {self.location.name} by {self.user.username} - {self.rating} stars"

    
class Booking(models.Model):
    location = models.ForeignKey(Location, related_name='bookings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_bookings', on_delete=models.CASCADE)
    booking_date = models.DateField()  # Start of the booking period
    order = models.ForeignKey(Order, related_name='order', on_delete=models.CASCADE, blank=True, null=True)


    class Meta:
        unique_together = ('location', 'booking_date',)  # Prevent overlapping bookings for the same location

    def __str__(self):
        return f"{self.user.username} booked {self.location.name} at {self.booking_date}"