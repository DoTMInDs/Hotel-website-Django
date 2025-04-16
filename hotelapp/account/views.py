from django.shortcuts import render,redirect
from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required 
from core.models import Lead,Manager,OurRoom
from .forms import CreateUserForm,UserUpdateForm,OurRoomForm

# Create your views here.
def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            print('there is an error')
            messages.error(request, "Please input a valid username and password")       

    return render(request, 'account/login.html')

def logout_user(request):
    logout(request)
    return render(request, 'core/base.html')
    

def sign_up(request):
    form = CreateUserForm()
    
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    
    context = {
        'form': form
    }
    return render(request, 'account/register.html', context)

@login_required
def profile(request):    
    
    if request.method == "POST":
        p_form = UserUpdateForm(request.POST, request.FILES, instance=request.user.profilemodel)
        if p_form.is_valid():
            p_form.save()
            return redirect('profile')
    else:
        p_form = UserUpdateForm(instance=request.user.profilemodel)
   
    context = {
        'p_form': p_form,
    }
    return render(request, 'dashboard/profile.html',context)

def dashboard(request):
    return render(request, 'dashboard/dashboard.html')

def leads(request):
    # try:   
    #     manager = request.user.manager
    # except Manager.DoesNotExist:
    #     messages.error(request, "You do not have manager permissions.")
    #     return redirect('dashboard')
    # if not manager.hotel_post:
    #     messages.error(request, "Your account is not linked to a hotel.")
    #     return redirect('dashboard')
    # leads = Lead.objects.filter(hotel=manager.hotel_post)

    context = {
        # "leads":leads
    }
    return render(request, 'dashboard/lead-table.html',context)

def add_room(request):
    try:
        manager = request.user.manager
    except Manager.DoesNotExist:
        messages.error(request, "You are not linked to a hotel.")
        return redirect('dashboard')
    
    if not manager.hotel_post:
        messages.error(request, "Your account is not linked to a hotel.")
        return redirect('dashboard')
    
    hotel = manager.hotel_post
    rooms = OurRoom.objects.filter(hotel=hotel)
    
    if request.method == "POST":
        form = OurRoomForm(request.POST, request.FILES)
        if form.is_valid():
           room = form.save(commit=False)
           room.hotel = hotel  # Assign the hotel automatically
           room.save()
           return redirect('dashboard')
    else:
        form = OurRoomForm()  
    context = {
        "form":form,
        "rooms":rooms
    }
    return render(request, "dashboard/add-room.html",context)

