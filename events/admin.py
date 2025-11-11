from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Event, Booking

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'venue', 'max_seats', 'available_seats', 'is_fully_booked', 'created_at')
    list_filter = ('date', 'venue')
    search_fields = ('title', 'venue')
    ordering = ('date',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'booking_date')
    list_filter = ('booking_date', 'event')
    search_fields = ('user__username', 'event__title')