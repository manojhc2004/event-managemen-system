from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.db.models import Count, Q 
from datetime import date
from .models import Event, Booking, UserProfile 
# FIX IS HERE: Importing the correct, renamed forms.
from .forms import UserUpdateForm, ProfileUpdateForm 

# ----------------------------------------------------
# 1. AUTHENTICATION (Registration)
# ----------------------------------------------------

class UserRegistrationView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # ✅ Let signal create profile automatically
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        return render(request, 'registration/register.html', {'form': form})

# ----------------------------------------------------
# 2. EVENT LISTING (Landing Page) - Includes Search Logic
# ----------------------------------------------------

class EventListView(ListView):
    """Displays a list of all upcoming events, with search functionality."""
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    ordering = ['date', 'time']

    def get_queryset(self):
        queryset = Event.objects.filter(date__gte=date.today())
        query = self.request.GET.get('q')
        
        if query:
            # Filter the queryset using Q objects for OR logic across fields
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(venue__icontains=query)
            ).distinct()
        return queryset.order_by('date', 'time')


# ----------------------------------------------------
# 3. EVENT DETAILS AND BOOKING
# ----------------------------------------------------

class EventDetailView(DetailView):
    """Displays a single event and its details."""
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        if self.request.user.is_authenticated:
            context['has_booked'] = Booking.objects.filter(
                user=self.request.user, 
                event=event
            ).exists()
        return context

class BookEventView(LoginRequiredMixin, View):
    """Handles the booking submission."""
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        if event.date < date.today():
            messages.error(request, 'Cannot book an event that has already passed.')
            return redirect('event_detail', pk=event.pk)

        if event.is_fully_booked():
            messages.error(request, f'{event.title} is fully booked. Sorry!')
            return redirect('event_detail', pk=event.pk)

        if Booking.objects.filter(user=request.user, event=event).exists():
            messages.warning(request, f'You have already booked a seat for {event.title}.')
            return redirect('event_detail', pk=event.pk)

        try:
            Booking.objects.create(user=request.user, event=event)
            messages.success(request, f'Successfully booked a seat for {event.title}!')
            return redirect('booking_confirmation', pk=event.pk)
        except Exception as e:
            messages.error(request, f'An error occurred during booking: {e}')
            return redirect('event_detail', pk=event.pk)

class BookingConfirmationView(LoginRequiredMixin, DetailView):
    """Displays a booking confirmation page."""
    model = Event
    template_name = 'events/booking_confirmation.html'
    context_object_name = 'event'


# ----------------------------------------------------
# 4. USER BOOKINGS
# ----------------------------------------------------

class MyBookingsView(LoginRequiredMixin, ListView):
    """Displays a list of events booked by the current user."""
    model = Booking
    template_name = 'events/my_bookings.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-booking_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        upcoming = []
        past = []
        for booking in context['bookings']:
            if booking.event.date >= date.today():
                upcoming.append(booking)
            else:
                past.append(booking)
        
        context['upcoming_bookings'] = upcoming
        context['past_bookings'] = past
        return context


# ----------------------------------------------------
# 5. USER PROFILE (Enhanced with ProfilePicture/Mobile)
# ----------------------------------------------------

class UserProfileView(LoginRequiredMixin, View):
    """Displays the user profile and handles form submission for updates."""
    
    def get(self, request):
        # Using the corrected form name
        user_form = UserUpdateForm(instance=request.user)
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        # Using the corrected form name
        profile_form = ProfileUpdateForm(instance=user_profile) 
        
        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, 'events/profile.html', context)

    def post(self, request):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        user_profile = request.user.userprofile
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile_view')
        else:
            messages.error(request, 'Please correct the errors below.')
            context = {
                'user_form': user_form,
                'profile_form': profile_form
            }
            return render(request, 'events/profile.html', context)


# ----------------------------------------------------
# 6. ADMIN DASHBOARD
# ----------------------------------------------------

def is_superuser(user):
    return user.is_superuser

@method_decorator(user_passes_test(is_superuser, login_url='/admin/login/'), name='dispatch')
class AdminDashboardView(LoginRequiredMixin, View):
    """Displays core statistics for administrators."""
    def get(self, request):
        total_events = Event.objects.count()
        total_bookings = Booking.objects.count()
        total_users = User.objects.count()
        
        recent_bookings = Booking.objects.select_related('user', 'event').order_by('-booking_date')[:5]
        
        event_stats = Event.objects.annotate(
            num_bookings=Count('booking')
        ).order_by('-num_bookings')[:5]

        context = {
            'total_events': total_events,
            'total_bookings': total_bookings,
            'total_users': total_users,
            'recent_bookings': recent_bookings,
            'event_stats': event_stats,
        }
        return render(request, 'events/admin_dashboard.html', context)