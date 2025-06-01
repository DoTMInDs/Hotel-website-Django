from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ValidationError

from .models import Room,Rating,Hotel,Reservation,Booking,Guest
from account.forms import LeadForm,ReservationForm,BookingForm

# Create your views here.

def index(request):
    l_form = LeadForm()
    
    if request.method == 'POST':
        l_form = LeadForm(request.POST)
        if l_form.is_valid():
            l_form.save()
            messages.success(request, 'Lead request successfull, We will Email you some details on how to login Thank you!!')
            return redirect('home')
        else:
            for field, errors in l_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        l_form = LeadForm()        
    
    context = {
        'l_form': l_form
    }
    return render(request, 'core/base.html',context)

def about(request):
    posts = Room.objects.all()[:5]
    ratings = Rating.objects.all()
    
    context = {
        'posts': posts,
        'ratings': ratings
    }
    return render(request, 'core/about.html', context)

def contact(request):
    form = LeadForm()
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully! We will Email you details to login in your Dashboard... Thank You!!')
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in all fields correctly.')
   
    context = {
        'form': form
    }
    return render(request, 'core/contact.html',context)

@login_required
def my_booking(request):
    bookings = Booking.objects.filter(guest__user=request.user).order_by('-created_at')
    reservations = Reservation.objects.filter(guest__user=request.user).order_by('-created_at')
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    context = {
        'bookings': page_obj,
        'reservations': reservations,
        'page_obj': page_obj,
    }
    return render(request, 'core/my_booking.html',context)

def hotel_rooms(request):
    hotels = Hotel.objects.all()
    name_query = request.GET.get('search', '')  # Hotel name search
    location_query = request.GET.get('loc-search', '')  # Location search
    if name_query or location_query:
        filters = Q()
        if name_query:
            filters &= Q(name__icontains=name_query)
        if location_query:
            filters &= Q(location__icontains=location_query)
        hotels = hotels.filter(filters)
    paginator = Paginator(hotels, 5)  # Show 10 hotels per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        page_obj = paginator.page(paginator.num_pages)
    context = {
        'hotels': hotels,
        'name_query': name_query,
        'location_query': location_query,
        'page_obj': page_obj,
    }
    return render(request, 'core/hotel_rooms.html',context)

def room_list(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    rooms = Room.objects.filter(hotel=hotel)
    name_query = request.GET.get('search', '')  # Hotel name search
    location_query = request.GET.get('loc-search', '')
    status_query = request.GET.get('status', '') 
    rating_query = request.GET.get('rating', '') 
    room_type_query = request.GET.get('room_type', '') 
    b_form = BookingForm()
    
    if name_query or location_query:
        filters = Q()
        if name_query:
            filters &= Q(hotel__name__icontains=name_query)
        if location_query:
            filters &= Q(hotel__location__icontains=location_query)
        if status_query:
            filters &= Q(status=status_query)
        if rating_query:
            filters &= Q(star_rating__star=rating_query)
        if room_type_query:
            filters &= Q(room_type=room_type_query)
        rooms = rooms.filter(filters)
    
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        b_form = BookingForm(request.POST)

        if room_id:
            room = get_object_or_404(Room, id=room_id)
            if b_form.is_valid():  # First validate the form
                booking = b_form.save(commit=False)
                booking.room = room
                # booking.guest, _ = Guest.objects.get_or_create(user=request.user)
                guest, created = Guest.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'first_name': request.user.first_name or 'Guest',
                        'last_name': request.user.last_name or 'User',
                        'email': request.user.email
                    }
                )
                booking.guest = guest
                try:
                    booking.save()  # This will trigger the clean() method
                    messages.success(request, 'Booking request submitted successfully!')
                    return redirect('room-list', pk=hotel.pk)
                except ValidationError as e:
                    for error in e.messages:
                        messages.error(request, error)
            else:
                for field, errors in b_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            messages.error(request, "Room ID missing in request.")
    else:
        b_form = BookingForm() 
        
    paginator = Paginator(rooms, 10)  # Show 10 rooms per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
        
    context = {
        'hotel': hotel,
        'rooms': rooms,
        'hotel_id': pk,
        'b_form': b_form,
        'name_query': name_query,
        'location_query': location_query,
        'status_query': status_query,
        'rating_query': rating_query,
        'room_type_query': room_type_query,
        'page_obj': page_obj,
        'status_choices': Room.ROOM_STATUS_CHOICES,
        'rating_choices': Rating.objects.all(), 
        'room_type_choices': Room.BED_TYPE_CHOICES,
    }
    return render(request, 'core/room_list.html', context)

def hotel(request):
    hotels = Hotel.objects.all()
    name_query = request.GET.get('search', '')  # Hotel name search
    location_query = request.GET.get('loc-search', '')  # Location search
    if name_query or location_query:
        filters = Q()
        if name_query:
            filters &= Q(name__icontains=name_query)
        if location_query:
            filters &= Q(location__icontains=location_query)
        hotels = hotels.filter(filters)
    paginator = Paginator(hotels, 3)  # Show 10 hotels per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        page_obj = paginator.page(paginator.num_pages)
    context = {
        'hotels': hotels,
        'name_query': name_query,
        'location_query': location_query,
        'page_obj': page_obj,
    }
    return render(request, 'core/hotel.html',context)

def hotel_services(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    services = hotel.services.all()
    context = {
        'hotel': hotel,
        'services': services
    }
    return render(request, 'core/hotel_services.html',context)

def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    context = {
        'room': room
    }
    return render(request, 'detail/room_detail.html',context)

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, guest__user=request.user)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted successfully!')
        return HttpResponseRedirect(reverse('my_booking'))
    return HttpResponseRedirect(reverse('my_booking'))