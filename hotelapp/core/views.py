from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required 
from django.core.paginator import Paginator,EmptyPage
from django.db.models import Q

from .models import OurRooms,Rating,HotelPost
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

@login_required
def about(request):
    posts = OurRooms.objects.all()
    ratings = Rating.objects.all()
    
    context = {
        'posts': posts,
        'ratings': ratings
    }
    return render(request, 'core/about.html', context)

@login_required
def contact(request):
    form = LeadForm()
    
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('about')
        else:
           form = LeadForm()        
    
    context = {
        'form': form
    }
    return render(request, 'core/contact.html',context)

@login_required
def booking(request):
    return render(request, 'core/booking.html')

@login_required
def hotel(request):
    posts = HotelPost.objects.all()
    p = Paginator(posts, 3)
    
    filter_query = request.GET.get('search') if request.GET.get('search') != None else ''
    posts = HotelPost.objects.filter(
        Q(name__icontains=filter_query) |
        Q(location__icontains=filter_query)        
    )
   
    page_num = request.GET.get("page", 1)
    try:
        page = p.page(page_num)
    except EmptyPage:
        page = p.page(1)
        
    context = {
        'posts': page,
    }
    return render(request, 'core/hotel.html',context)


@login_required
def detail(request, pk):
    posts = HotelPost.objects.get(id=pk)
    context = {
        'posts': posts
    }
    return render(request, 'detail/detail.html',context)