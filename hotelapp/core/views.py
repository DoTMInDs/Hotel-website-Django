from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required 
from django.core.paginator import Paginator,EmptyPage
from django.db.models import Q
from django.contrib import messages

from .models import OurRoom,Rating,HotelPost
from account.forms import LeadForm

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
def booking(request):
    return render(request, 'core/booking.html')

def room(request):
    rooms = OurRoom.objects.all()
    context = {
        'rooms': rooms,
    }
    return render(request, 'core/room.html',context)

def hotel(request):
    hotels = HotelPost.objects.all()
    context = {
        'hotels': hotels,
    }
    return render(request, 'core/hotel.html',context)

def detail(request, pk):
    posts = HotelPost.objects.get(id=pk)
    context = {
        'posts': posts
    }
    return render(request, 'detail/detail.html',context)