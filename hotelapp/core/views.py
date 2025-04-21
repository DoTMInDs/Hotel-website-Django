from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import OurRoom,Rating,HotelPost,Booking
from account.forms import LeadForm,BookRoomForm

# Create your views here.

def index(request):
    l_form = LeadForm()
    
    if request.method == 'POST':
        l_form = LeadForm(request.POST)
        if l_form.is_valid():
            l_form.save()
            return redirect('home')
        else:
           l_form = LeadForm()        
    
    context = {
        'l_form': l_form
    }
    return render(request, 'core/base.html',context)

def about(request):
    posts = OurRoom.objects.all()
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
            messages.success(request, 'You message has been sent successfully!')
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in all fields correctly.')
   
    context = {
        'form': form
    }
    return render(request, 'core/contact.html',context)

@login_required
def my_booking(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
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
        'page_obj': page_obj,
    }
    return render(request, 'core/my_booking.html',context)

def room(request):
    rooms = OurRoom.objects.all()
    name_query = request.GET.get('search', '')  # Hotel name search
    location_query = request.GET.get('loc-search', '')
    b_form = BookRoomForm()
    if name_query or location_query:
        filters = Q()
        if name_query:
            filters &= Q(hotel__name__icontains=name_query)
        if location_query:
            filters &= Q(hotel__location__icontains=location_query)
        rooms = rooms.filter(filters)
    if request.method == 'POST':
        room_id = request.POST.get('room')
        room = get_object_or_404(OurRoom, id=room_id)
        b_form = BookRoomForm(request.POST)
        if b_form.is_valid():
            booking = b_form.save(commit=False)
            booking.user = request.user
            booking.room = room
            booking.hotel = room.hotel
            booking.save()
            messages.success(request, f'Booking successful for {room.room_type} at {room.hotel.name}!')
            return redirect('room')
        else:
            messages.error(request, 'Please fill in all fields correctly.')
    else:
        b_form = BookRoomForm()
        print('error message')
    
    paginator = Paginator(rooms, 10)  # Show 10 rooms per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    context = {
        'rooms': rooms,
        'b_form': b_form,
        'name_query': name_query,
        'location_query': location_query,
        'page_obj': page_obj,
    }
    return render(request, 'core/room.html',context)

def hotel(request):
    hotels = HotelPost.objects.all()
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

def room_detail(request, pk):
    room = get_object_or_404(OurRoom, pk=pk)
    context = {
        'room': room
    }
    return render(request, 'detail/room_detail.html',context)

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted successfully!')
        return HttpResponseRedirect(reverse('my_booking'))
    return HttpResponseRedirect(reverse('my_booking'))