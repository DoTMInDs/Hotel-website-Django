from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required 
from core.models import Manager,Room,Staff,Guest,Reservation,Amenity,Hotel,Service
from .forms import CreateUserForm,UserUpdateForm,RoomForm,StaffForm,ReservationForm,HotelForm,AddAmenitiesForm,ServiceForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def get_manager_hotel(user):
    try:
        return user.manager.hotel_post
    except Manager.DoesNotExist:
        return None
    except AttributeError:
        return None
# Create your views here.
def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            Guest.objects.get_or_create(user=user)
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

def manage_hotel_account(request):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')
    hotel_form = HotelForm(instance=hotel)
    amenities_form = AddAmenitiesForm()
    if request.method == "POST":
        if 'hotel_submit' in request.POST:
            hotel_form = HotelForm(request.POST, request.FILES, instance=hotel)
            if hotel_form.is_valid():
                hotel_form.save()
                messages.success(request, "Hotel information updated successfully!")
                return redirect('manage-hotel-account')
        
        elif 'amenity_submit' in request.POST:
            amenities_form = AddAmenitiesForm(request.POST)
            if amenities_form.is_valid():
                amenity = amenities_form.save(commit=False)
                
                # Check if amenity already exists for this hotel
                existing_amenity = Amenity.objects.filter(
                    amenity_name__iexact=amenity.amenity_name,
                    hotels=hotel
                ).first()
                
                if existing_amenity:
                    messages.info(request, f"Amenity '{amenity.amenity_name}' already exists for your hotel.")
                else:
                    amenity.save()
                    hotel.amenities.add(amenity)
                    messages.success(request, "Amenity added successfully!")
                
                return redirect('manage-hotel-account')
    
    context = {
        'hotel_form': hotel_form,
        'amenities_form': amenities_form,
        'hotel': hotel,
    }
    return render(request, 'dashboard/manage-hotel-account.html',context)

def remove_amenity(request, amenity_id):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')
    
    amenity = get_object_or_404(Amenity, id=amenity_id)
    hotel.amenities.remove(amenity)
    messages.success(request, f"Amenity '{amenity.amenity_name}' removed successfully!")
    return redirect('manage-hotel-account')

def manage_account(request):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')
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
    return render(request, 'dashboard/manage-account.html',context)

@login_required
def dashboard(request):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')
    
    staff_members = Staff.objects.filter(hotel=hotel).order_by('-join_date')
    reservations = Reservation.objects.filter(room__hotel=hotel.id).order_by('-created_at')
    rooms = Room.objects.filter(hotel=hotel).order_by('-created_at')
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
        "reservations": reservations,
        "rooms": rooms,
    }
    return render(request, 'dashboard/dashboard.html',context)

@login_required
def guest(request):
    try:
        manager = request.user.manager
        hotel = manager.hotel_post
        if not hotel:
            messages.error(request, "Your hotel is not assigned.")
            return redirect('home')
    except (Manager.DoesNotExist, AttributeError):
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')
    guests = Reservation.objects.filter(room__hotel=hotel.id).order_by('-created_at')
    
    paginator = Paginator(guests, 10)  # Show 10 guest per page
    page_number = request.GET.get('page')
    paginator = Paginator(guests, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
        
    context = {
        "guests": page_obj,
        "hotel": hotel,
        "page_obj": page_obj, 
    }
    return render(request, 'dashboard/guest.html',context)

@login_required
def reservation(request):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')

    # Initialize form with hotel context
    r_form = ReservationForm(hotel=hotel)
    
    if request.method == 'POST':
        if 'update_status' in request.POST:
            # Handle status update logic
            reservation_id = request.POST.get('reservation_id')
            new_status = request.POST.get('status')
            try:
                reservation = Reservation.objects.get(id=reservation_id, room__hotel=hotel)
                reservation.status = new_status
                reservation.save()
                
                # Update room status
                if new_status == 'Checked In':
                    reservation.room.status = 'Occupied'
                    reservation.room.save()
                elif new_status in ['Checked Out', 'Cancelled']:
                    reservation.room.status = 'Available'
                    reservation.room.save()
                    
                messages.success(request, "Reservation status updated successfully!")
            except Reservation.DoesNotExist:
                messages.error(request, "Reservation not found")
        else:
            # Handle new reservation creation
            r_form = ReservationForm(request.POST, hotel=hotel)
            if r_form.is_valid():
                try:
                    # Create reservation instance from form but don't save yet
                    reservation = r_form.save(commit=False)

                    # --- Start of modified code ---

                    # 1. Extract guest information from the form
                    guest_first_name = r_form.cleaned_data['first_name']
                    guest_last_name = r_form.cleaned_data['last_name']
                    guest_email = r_form.cleaned_data.get('email')
                    guest_phone = r_form.cleaned_data.get('phone_number')

                    # 2. Try to find an existing Guest or create a new one
                    guest_instance = None
                    if guest_email:
                        # Try finding by email first if available
                        guest_instance = Guest.objects.filter(email=guest_email).first()

                    if not guest_instance and guest_first_name and guest_last_name:
                        # If not found by email, try finding by name and phone (if phone is provided)
                        filter_kwargs = {
                            'first_name__iexact': guest_first_name,
                            'last_name__iexact': guest_last_name,
                        }
                        if guest_phone:
                             filter_kwargs['phone_number'] = guest_phone

                        guest_instance = Guest.objects.filter(**filter_kwargs).first()

                    # If guest doesn't exist, create a new one
                    if not guest_instance:
                        guest_instance = Guest.objects.create(
                            first_name=guest_first_name,
                            last_name=guest_last_name,
                            email=guest_email,
                            phone_number=guest_phone,
                            # Add other guest fields if needed from the form or defaults
                        )

                    # 3. Assign the found or created guest instance to the reservation
                    reservation.guest = guest_instance

                    # --- End of modified code ---

                    reservation.hotel = hotel # Assuming Reservation model has a hotel field

                    # Calculate pricing
                    num_nights = (reservation.check_out_date - reservation.check_in_date).days
                    # Add validation or handling for num_nights <= 0 if necessary
                    reservation.price_per_night_at_booking = reservation.room.price
                    reservation.total_price = num_nights * reservation.room.price if num_nights > 0 else reservation.room.price

                    reservation.save()

                    messages.success(request, "Reservation created successfully!")
                    return redirect('reservation')
                except ValidationError as e:
                     messages.error(request, f"Validation Error: {e.messages[0]}")
                except Exception as e:
                    messages.error(request, f"Error creating reservation: {str(e)}")
            else:
                # Form is not valid, errors will be in r_form.errors
                for field, errors in r_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")

    # Get paginated reservations
    reservations = Reservation.objects.filter(room__hotel=hotel).order_by('-created_at')
    paginator = Paginator(reservations, 10)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        "reservations": page_obj,
        "hotel": hotel,
        "page_obj": page_obj,
        "r_form": r_form,
        "status_choices": Reservation.STATUS_CHOICES,
    }
    return render(request, 'dashboard/reservation.html', context)

@login_required
def add_room(request):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')
    rooms = Room.objects.filter(hotel=hotel).order_by('-created_at')
    
    paginator = Paginator(rooms, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    if request.method == "POST":
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
           room = form.save(commit=False)
           room.hotel = hotel  
           room.save()
           messages.success(request, "Room added successfully!")
           return redirect('dashboard')
        else:
           messages.error(request, "Room failed to save! Check your form...")
    else:
        form = RoomForm()  
    context = {
        "form":form,
        "rooms": page_obj,
        "hotel": hotel,
        "page_obj": page_obj, 
    }
    return render(request, "dashboard/add-room.html",context)

@login_required
def edit_reservation(request, pk):
    manager_hotel = get_manager_hotel(request.user)
    if not manager_hotel:
        messages.error(request, "You are not registered as a hotel manager or your hotel is not assigned.")
        return redirect('home')

    reservation = get_object_or_404(Reservation, pk=pk, room__hotel=manager_hotel)

    if request.method == "POST":
        form = ReservationForm(request.POST, instance=reservation, hotel=manager_hotel)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Reservation #{reservation.id} updated successfully!")
                return redirect('reservation') # Redirect to the list view
            except ValidationError as e:
                 messages.error(request, f"Error saving reservation: {e.messages[0]}") # Display first error message
                 context = {
                     'form': form,
                     'reservation': reservation,
                     'hotel': manager_hotel,
                     'page_title': _("Edit Reservation"),
                 }
                 return render(request, 'dashboard/edit-reservation.html', context)

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ReservationForm(instance=reservation, hotel=manager_hotel)

    context = {
        'form': form,
        'reservation': reservation,
        'hotel': manager_hotel,
        'page_title': _("Edit Reservation"), # Use gettext_lazy for translatable string
    }
    return render(request, 'dashboard/edit-reservation.html', context)

def services(request):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager or your hotel is not found.")
        return redirect('home')
    services = hotel.services.all().order_by('category', 'name')
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            # Service is created but not yet saved to the database
            service.save() # Save the service first
            # Now add the service to the hotel's many-to-many relationship
            hotel.services.add(service)

            messages.success(request, f"Service '{service.name}' added successfully to {hotel.name}!")
            return redirect('services') # Redirect to the service list

    else: # GET request
        form = ServiceForm()
    context = {
        'hotel': hotel,
        'form': form,
        'services': services,
        'title': f"{hotel.name} Services" # Dynamic title
    }
    return render(request, 'dashboard/services.html',context)

@login_required
def edit_service(request, pk):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager or your hotel is not found.")
        return redirect('home')

    # Get the service instance, ensuring it's associated with the manager's hotel
    service = get_object_or_404(Service, pk=pk)

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save() 

            messages.success(request, f"Service '{service.name}' updated successfully for {hotel.name}!")
            return redirect('services') # Redirect to the service list

    else: # GET request
        form = ServiceForm(instance=service) 

    context = {
        'hotel': hotel,
        'form': form,
        'service': service, 
        'title': f"Edit Service: {service.name}"
    }
    return render(request, 'dashboard/edit-service.html', context)



def add_room_detail(request, pk):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')
    room = get_object_or_404(Room, pk=pk, hotel=hotel)
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
    room = get_object_or_404(Room, pk=pk, hotel=hotel)
    if request.method == "POST":
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, "Room updated successfully!")
            return redirect('add-room-detail', pk=room.id)
    else:
        form = RoomForm(instance=room)
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

@login_required
def delete_reservation(request, reservation_id):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')
    reservation = get_object_or_404(Reservation, id=reservation_id, room__hotel=hotel)
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, 'Reservation deleted successfully!')
        return redirect('reservation')
    return redirect('reservation')

@login_required
def delete_service(request, service_id):
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')
    service = get_object_or_404(Service.objects.filter(), pk=service_id)
    if request.method == "POST":
        service.delete()
        messages.success(request, 'Reservation deleted successfully!')
        return redirect('services')
    return redirect('services')