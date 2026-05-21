import os
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from dotenv import load_dotenv

from .forms import CustomerRegistrationForm, HotelRegistrationForm
from .models import (Booking, Customer, Guide, Hotel, HotelOwner, Room, Trip,
                     UserProfile)

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


# ---------------------------------------------------------------------------
# General pages
# ---------------------------------------------------------------------------

def index(request):
    return render(request, 'index.html')


def base(request):
    return render(request, 'base.html')


def dashboard(request):
    return render(request, 'dashboard.html')


def destinations(request):
    return render(request, 'destinations.html')


def comments(request):
    return render(request, 'comments.html')


def gallery(request):
    return render(request, 'gallery.html')


def packages(request):
    return render(request, 'packages.html')


def about_us(request):
    return render(request, 'about_us.html')


def contact_us(request):
    return render(request, 'contact_us.html')


def equipment(request):
    return render(request, 'equipment.html')


def payment(request):
    return render(request, 'payment.html')


def maps(request):
    return render(request, 'maps.html')

def booknow(request):
    return render(request, 'booknow.html')


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password1'])
            user.save()

            role = form.cleaned_data['role']
            UserProfile.objects.create(user=user, role=role)
            login(request, user)

            return redirect('dashboard' if role == 'hotel_owner' else 'index')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


# ---------------------------------------------------------------------------
# Hotel
# ---------------------------------------------------------------------------

def HotelList(request):
    # FIX: Hotel has no 'rating' field — removed invalid order_by
    hotels = Hotel.objects.all()
    return render(request, 'hotels.html', {'hotels': hotels})


@login_required
def HotelRegistration(request):
    if request.method == 'POST':
        form = HotelRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hotel registered successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = HotelRegistrationForm()

    return render(request, 'hotel_reg_form.html', {'form': form})


def search(request):
    query = request.GET.get('search', '')
    hotels = Hotel.objects.filter(name__icontains=query) if query else Hotel.objects.all()
    return render(request, 'search.html', {'query': query, 'hotel': hotels})


@login_required
def EditHotel(request, pk):
    hotel = get_object_or_404(Hotel, id=pk)
    if request.method == 'POST':
        form = HotelRegistrationForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hotel updated successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = HotelRegistrationForm(instance=hotel)

    return render(request, 'hotel_reg_form.html', {'form': form})


@login_required
def deleteHotel(request, pk):
    if request.method == 'POST':
        # FIX: Hotel has no user field — removed user=request.user filter
        hotel = get_object_or_404(Hotel, id=pk)
        hotel.delete()
        messages.success(request, 'Hotel deleted successfully!')
    return redirect('hotels')


# ---------------------------------------------------------------------------
# Guide
# ---------------------------------------------------------------------------

@login_required
def deleteGuide(request, pk):
    if request.method == 'POST':
        # FIX: Guide has no user field — removed user=request.user filter
        guide = get_object_or_404(Guide, id=pk)
        guide.delete()
        messages.success(request, 'Guide deleted successfully!')
    return redirect('dashboard')


# ---------------------------------------------------------------------------
# Booking
# ---------------------------------------------------------------------------

@login_required
def book_room(request, hotel_id):
    hotel  = get_object_or_404(Hotel, id=hotel_id)
    rooms  = Room.objects.filter(hotel=hotel, available_rooms__gt=0)
    guides = Guide.objects.filter(is_available=True)

    if request.method == 'POST':
        room_id    = request.POST.get('room_id')
        guide_id   = request.POST.get('guide_id')
        check_in   = request.POST.get('check_in')
        check_out  = request.POST.get('check_out')
        num_rooms  = int(request.POST.get('num_rooms', 1))

        room = get_object_or_404(Room, id=room_id)

        if room.available_rooms < num_rooms:
            messages.error(request, 'Not enough rooms available!')
            return redirect('book_room', hotel_id=hotel_id)

        nights = (datetime.strptime(check_out, '%Y-%m-%d') -
                  datetime.strptime(check_in,  '%Y-%m-%d')).days

        if nights <= 0:
            messages.error(request, 'Check-out must be after check-in.')
            return redirect('book_room', hotel_id=hotel_id)

        total = room.price * nights * num_rooms

        guide = None
        if guide_id:
            guide = get_object_or_404(Guide, id=guide_id)
            # FIX: was guide.price — correct field is price_per_day
            total += guide.price_per_day * nights

        booking = Booking.objects.create(
            user=request.user,
            hotel=hotel,
            room=room,
            guide=guide,
            check_in=check_in,
            check_out=check_out,
            num_rooms=num_rooms,
            total_price=total,
        )

        room.available_rooms -= num_rooms
        room.save()

        try:
            send_mail(
                subject='Booking Confirmation',
                message=f'Your booking for {booking.room} is confirmed! Total: ${total}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=False,
            )
        except Exception:
            pass  # Don't let email failure break the booking flow

        messages.success(request, f'Booking confirmed! Total: ${total}')
        return redirect('booking_success', booking_id=booking.id)

    return render(request, 'booking_form.html', {
        'hotel': hotel,
        'rooms': rooms,
        'guides': guides,
    })


@login_required
def cancel_booking(request, booking_id):
    # FIX: was missing booking_id param — now correctly received from URL
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    booking.room.available_rooms += booking.num_rooms
    booking.room.save()
    booking.delete()

    messages.success(request, 'Booking cancelled!')
    return redirect('hotels')


def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_success.html', {'booking': booking})


# ---------------------------------------------------------------------------
# Customer / Owner profile
# ---------------------------------------------------------------------------

@login_required
def customerDetails(request):
    # FIX: was get_object_or_404(user=request.user) — missing model arg
    customer = get_object_or_404(Customer, user=request.user)
    return render(request, 'customer_details.html', {'customer': customer})


@login_required
def hotelOwnerdetails(request):
    hotel_owner = get_object_or_404(HotelOwner, user=request.user)
    return render(request, 'hotel_owner_details.html', {'hotel_owner': hotel_owner})


# ---------------------------------------------------------------------------
# Trip / Map  (FIX: removed duplicate route() definition)
# ---------------------------------------------------------------------------

def create_trip(request):
    """
    Two entry points:

    1. booknow form (no coords yet):
       pickup + destination text only → save Trip → redirect to maps
       maps.html reads the GET params, pre-fills the search boxes,
       auto-geocodes both locations, and shows the "View Route & Hotels" button.

    2. maps.html "View Route & Hotels" form (coords confirmed):
       all fields including lat/lng → save Trip → redirect to route/<id>/
    """
    if request.method == 'GET':
        pickup          = request.GET.get('pickup', '').strip()
        destination     = request.GET.get('destination', '').strip()
        pickup_lat      = request.GET.get('pickup_lat', '').strip()
        pickup_lng      = request.GET.get('pickup_lng', '').strip()
        destination_lat = request.GET.get('destination_lat', '').strip()
        destination_lng = request.GET.get('destination_lng', '').strip()
        people          = request.GET.get('people', '1').strip()
        days            = request.GET.get('days', '1').strip()

        if not pickup or not destination:
            messages.error(request, 'Please enter both pickup and destination.')
            return redirect('maps')

        try:
            people_int = int(people)
            days_int   = int(days)
        except ValueError:
            messages.error(request, 'People and days must be numbers.')
            return redirect('maps')

        has_coords = pickup_lat and pickup_lng and destination_lat and destination_lng

        if has_coords:
            # Coming from maps.html — save full trip and go to route summary
            trip = Trip.objects.create(
                user            = request.user if request.user.is_authenticated else None,
                fullname        = request.GET.get('fullname', ''),
                email           = request.GET.get('email', ''),
                pickup          = pickup,
                destination     = destination,
                pickup_lat      = float(pickup_lat),
                pickup_lng      = float(pickup_lng),
                destination_lat = float(destination_lat),
                destination_lng = float(destination_lng),
                people          = people_int,
                days            = days_int,
            )
            return redirect('route', trip_id=trip.id)

        else:
            # Coming from booknow form — no coords yet.
            # Don't save a trip yet; just send the user to maps with their
            # text pre-filled so they can confirm the route on the map first.
            from urllib.parse import urlencode
            params = urlencode({
                'pickup':      pickup,
                'destination': destination,
                'fullname':    request.GET.get('fullname', ''),
                'email':       request.GET.get('email', ''),
                'people':      people_int,
                'days':        days_int,
            })
            return redirect(f'/reserve/maps/?{params}')

    return redirect('maps')


def route(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    hotels = Hotel.objects.filter(location__icontains=trip.destination, available_rooms__gt=0)
    if not hotels.exists():
        hotels = Hotel.objects.filter(available_rooms__gt=0)[:6]
    return render(request, "route.html", {"trip": trip, "hotels": hotels})