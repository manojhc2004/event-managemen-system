from django.urls import path
from . import views

urlpatterns = [
    # AUTH URLS
    path('register/', views.UserRegistrationView.as_view(), name='register'),

    # MAIN EVENT URLS
    path('', views.EventListView.as_view(), name='event_list'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('event/<int:pk>/book/', views.BookEventView.as_view(), name='book_event'),
    path('event/<int:pk>/confirm/', views.BookingConfirmationView.as_view(), name='booking_confirmation'),
    
    # USER PAGES URLS
    path('my-bookings/', views.MyBookingsView.as_view(), name='my_bookings'),
    path('profile/', views.UserProfileView.as_view(), name='profile_view'),
    
    # ADMIN URL
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
]