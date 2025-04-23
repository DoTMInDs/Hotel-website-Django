from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required 
from core.models import Booking,Manager,OurRoom,Staff
from .forms import CreateUserForm,UserUpdateForm,OurRoomForm,StaffForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.urls import reverse

def get_manager_hotel(user):
    try:
        return user.manager.hotel_post
    except Manager.DoesNotExist:
        return None
# Create your views here.
def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "Logged In successfully!!")
            return redirect('home')
        else:
            print('there is an error')
            messages.error(request, "Please input a valid username and password!!") 
                

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
            messages.success(request, "You have successfully registered an account!!")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")  
    
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
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Your data wasn't saved.. Please check your form!!")
    else:
        p_form = UserUpdateForm(instance=request.user.profilemodel)
   
    context = {
        'p_form': p_form,
    }
    return render(request, 'dashboard/profile.html',context)

@login_required
def dashboard(request):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('dashboard')
    
    staff_members = Staff.objects.filter(hotel=hotel).order_by('-join_date')
    leads = Booking.objects.filter(hotel=hotel.id).order_by('-created_at')
    rooms = OurRoom.objects.filter(hotel=hotel).order_by('-created_at')
    form = StaffForm()
    
    if request.method == "POST":
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            staff = form.save(commit=False)
            staff.hotel = hotel
            staff.save()
            messages.success(request, "Staff member added successfully!")
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    context = {
        'staff_members': staff_members,
        'staff_form': form,
        'hotel': hotel,
        "leads": leads,
        "rooms": rooms,
    }
    return render(request, 'dashboard/dashboard.html',context)

@login_required
def leads(request):
    try:
        manager = request.user.manager
        hotel = manager.hotel_post
    except (Manager.DoesNotExist, AttributeError):
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')
    leads = Booking.objects.filter(hotel=hotel.id).order_by('-created_at')
    
    paginator = Paginator(leads, 10)  # Show 10 leads per page
    page_number = request.GET.get('page')
    paginator = Paginator(leads, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
        
    context = {
        "leads": page_obj,
        "hotel": hotel,
        "page_obj": page_obj, 
    }
    return render(request, 'dashboard/lead-table.html',context)

@login_required
def add_room(request):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('dashboard')
    rooms = OurRoom.objects.filter(hotel=hotel).order_by('-created_at')
    
    paginator = Paginator(rooms, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    if request.method == "POST":
        form = OurRoomForm(request.POST, request.FILES)
        if form.is_valid():
           room = form.save(commit=False)
           room.hotel = hotel  
           room.save()
           messages.success(request, "Room added successfully!")
           return redirect('dashboard')
        else:
           messages.error(request, "Room failed to save! Check your form...")
    else:
        form = OurRoomForm()  
    context = {
        "form":form,
        "rooms": page_obj,
        "hotel": hotel,
        "page_obj": page_obj, 
    }
    return render(request, "dashboard/add-room.html",context)

def add_room_detail(request, pk):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('dashboard')
    room = get_object_or_404(OurRoom, pk=pk, hotel=hotel)
    context = {
       'hotel':hotel,
       'room': room,
    }
    return render(request, 'dashboard/room-detail/add-room-detail.html',context)

def edit_room(request, pk):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')
    room = get_object_or_404(OurRoom, pk=pk, hotel=hotel)
    if request.method == "POST":
        form = OurRoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, "Room updated successfully!")
            return redirect('add-room-detail', pk=room.id)
    else:
        form = OurRoomForm(instance=room)
    context = {
        'form': form,
        'room': room,
        'hotel': hotel,
    }
    return render(request, 'dashboard/room-detail/edit-room.html', context)

@login_required
def edit_staff(request, pk):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')
    staff = get_object_or_404(Staff, pk=pk, hotel=hotel)
    if request.method == "POST":
        form = StaffForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff member updated successfully!")
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = StaffForm(instance=staff)
    
    context = {
        'form': form,
        'staff': staff,
        'hotel': hotel,
    }
    return render(request, 'dashboard/edit-staff.html', context)

@login_required
def toggle_staff(request, pk):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')
    
    staff = get_object_or_404(Staff, pk=pk, hotel=hotel)
    staff.is_active = not staff.is_active
    staff.save()
    
    messages.success(request, f"Staff member {'activated' if staff.is_active else 'deactivated'} successfully!")
    return redirect('dashboard')

@login_required
def delete_staff(request, staff_id):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')
    staff = get_object_or_404(Staff, id=staff_id, hotel=hotel)
    if request.method == 'POST':
        staff.delete()
        messages.success(request, 'Staff deleted successfully!')
        return redirect('dashboard')
    return redirect('dashboard')