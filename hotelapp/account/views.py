from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test 
from .models import ProfileModel
from core.models import CustomUser,Manager,Room,Staff,Guest,Reservation,Amenity,Hotel,Service,Booking,OurRoomsImage
from .forms import CreateUserForm,UserUpdateForm,RoomForm,StaffForm,ReservationForm,HotelForm,AddAmenitiesForm,ServiceForm,RoomGalleryForm,BulkRoomGalleryForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .utils import send_welcome_email
import cloudinary.uploader

def get_manager_hotel(user):
    try:
        return user.manager.hotel_post
    except Manager.DoesNotExist:
        return None
    except AttributeError:
        return None

def staff_required(view_func):
    """
    Decorator to ensure user is staff and superuser
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff or not request.user.is_superuser:
            messages.error(request, "You do not have permission to access this page.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

# Create your views here.
def login_user(request):
    if 'next' in request.GET:
        messages.warning(request, "Your session expired due to inactivity. Please log in again.")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            Guest.objects.get_or_create(user=user)
            messages.success(request, "Logged In successfully!!")
            if user.user_type == 'manager':
                return redirect('dashboard')
            elif user.is_staff and user.is_superuser:
                return redirect('staff_dashboard')
            else:
                return redirect('home')
        else:
            print('there is an error')
            messages.error(request, "Please input a valid username and password!!") 

    return render(request, 'account/login.html')

def logout_user(request):
    logout(request)
    messages.success(request, "Logged Out successfully!!")
    return redirect('home')
    

def sign_up(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Activate user immediately
            user.is_verified = True  # Mark user as verified
            user.user_type = 'Guest'  # Set user type to 'Guest'
            user.save()

            # Send welcome email
            try:
                send_welcome_email(user)
            except Exception as e:
                # Log the error but don't prevent registration
                print(f"Error sending welcome email: {e}")

            messages.success(request, "You have successfully registered an account!!")
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Failed to authenticate after registration")
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
            for field, errors in p_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
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
                try:
                    hotel_form.save()
                    messages.success(request, "Hotel information updated successfully!")
                    return redirect('manage-hotel-account')
                except Exception as e:
                    messages.error(request, f"Error saving hotel information: {str(e)}")
            else:
                for field, errors in hotel_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        
        elif 'amenity_submit' in request.POST:
            amenities_form = AddAmenitiesForm(request.POST)
            if amenities_form.is_valid():
                amenity = amenities_form.save(commit=False)
                existing = Amenity.objects.filter(
                    amenity_name__iexact=amenity.amenity_name,
                    hotels=hotel
                ).first()

                if existing:
                    messages.info(request, f"Amenity '{amenity.amenity_name}' already exists.")
                else:
                    amenity.save()
                    hotel.amenities.add(amenity)
                    messages.success(request, "Amenity added successfully!")
                return redirect('manage-hotel-account')
            else:
                for field, errors in amenities_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
    
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
    
    profile, created = ProfileModel.objects.get_or_create(user=request.user)
    if request.method == "POST":
        p_form = UserUpdateForm(request.POST, request.FILES, instance=request.user.profilemodel)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('manage-account')
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
    guests = Booking.objects.filter(room__hotel=hotel.id).order_by('-created_at')
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
        "guests": guests,
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
    
    guests = Booking.objects.filter(room__hotel=hotel.id).order_by('-created_at')
    
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
           return redirect('add-room')
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




# Staff Dasboard
def staff_dashboard(request):
    if not request.user.is_staff or not request.user.is_superuser:
        messages.error(request, "You do not have permission to access the staff dashboard.")
        return redirect('home')
    
    return render(request, "staff/dashboard/staff_dashboard.html")

@login_required
@staff_required
def user_management(request):
    """
    Main user management view with filtering and search
    """
    # Get all users - remove problematic prefetch_related
    users = CustomUser.objects.select_related(
        'manager', 
        'guest_profile'
    ).all().order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Filter by user type
    user_type = request.GET.get('user_type', '')
    if user_type:
        users = users.filter(user_type=user_type)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    elif status_filter == 'verified':
        users = users.filter(is_verified=True)
    elif status_filter == 'unverified':
        users = users.filter(is_verified=False)

    # create User Form
    if request.method == 'POST':
        form = UserUpdateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Set password if provided
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            
            messages.success(request, f"User {user.username} created successfully!")
            return redirect('user_management')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserUpdateForm()
    
    # Pagination
    paginator = Paginator(users, 10)  # 10 users per page
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Get user statistics
    user_stats = {
        'total_users': CustomUser.objects.count(),
        'active_users': CustomUser.objects.filter(is_active=True).count(),
        'verified_users': CustomUser.objects.filter(is_verified=True).count(),
        'admin_users': CustomUser.objects.filter(user_type='admin').count(),
        'manager_users': CustomUser.objects.filter(user_type='manager').count(),
        'staff_users': CustomUser.objects.filter(user_type='staff').count(),
        'guest_users': CustomUser.objects.filter(user_type='Guest').count(),
    }
    
    context = {
        'form': form,
        'users': page_obj,
        'page_obj': page_obj,
        'user_stats': user_stats,
        'search_query': search_query,
        'page_title': "Create New User",
        'selected_user_type': user_type,
        'selected_status': status_filter,
        'user_type_choices': CustomUser.USER_TYPE_CHOICES,
    }
    
    return render(request, "staff/dashboard/user_management.html", context)

@login_required
@staff_required
def user_detail(request, user_id):
    """
    View individual user details
    """
    user = get_object_or_404(CustomUser, id=user_id)

    user_type = request.GET.get('user_type', '')
    if user_type:
        users = users.filter(user_type=user_type)
    
    # Get related data based on user type
    related_data = {}
    
    if user.user_type == 'manager':
        try:
            related_data['manager_profile'] = user.manager
            related_data['hotel'] = user.manager.hotel_post
        except Manager.DoesNotExist:
            related_data['manager_profile'] = None
            related_data['hotel'] = None
    
    elif user.user_type == 'staff':
        # For staff users, get their staff profiles
        related_data['staff_profiles'] = Staff.objects.filter(email=user.email)
    
    elif user.user_type == 'Guest':
        try:
            related_data['guest_profile'] = user.guest_profile
        except Guest.DoesNotExist:
            related_data['guest_profile'] = None
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"User {user.username} updated successfully!")
            return redirect('user_management')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserUpdateForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
        'related_data': related_data,
        'page_title': f"Edit User: {user.username}",
        'selected_user_type': user_type,
        'user_type_choices': CustomUser.USER_TYPE_CHOICES,
    }
    
    return render(request, "staff/dashboard/user_detail.html", context)


@login_required
@staff_required
def toggle_user_status(request, user_id):
    """
    Toggle user active status
    """
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        
        action = "activated" if user.is_active else "deactivated"
        messages.success(request, f"User {user.username} has been {action}.")
    
    return redirect('user_management')

@login_required
@staff_required
def toggle_verification(request, user_id):
    """
    Toggle user verification status
    """
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        user.is_verified = not user.is_verified
        user.save()
        
        action = "verified" if user.is_verified else "unverified"
        messages.success(request, f"User {user.username} has been {action}.")
    
    return redirect('user_management')

@login_required
@staff_required
def delete_user(request, user_id):
    """
    Delete a user account
    """
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"User {username} has been deleted successfully.")
        return redirect('user_management')
    
    context = {
        'user': user,
    }
    
    return render(request, "staff/dashboard/confirm_delete.html", context)

@login_required
@staff_required
def manage_staff(request):
    """
    Manage staff members across all hotels
    """
    staff_members = Staff.objects.select_related('hotel', 'user').all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        staff_members = staff_members.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(hotel__name__icontains=search_query) |
            Q(position__icontains=search_query)
        )
    
    # Filter by department
    department = request.GET.get('department', '')
    if department:
        staff_members = staff_members.filter(department=department)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        staff_members = staff_members.filter(is_active=True)
    elif status_filter == 'inactive':
        staff_members = staff_members.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(staff_members, 10)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Staff statistics
    staff_stats = {
        'total_staff': Staff.objects.count(),
        'active_staff': Staff.objects.filter(is_active=True).count(),
        'by_department': Staff.objects.values('department').annotate(count=Count('id')),
        'by_position': Staff.objects.values('position').annotate(count=Count('id')),
    }
    
    context = {
        'staff_members': page_obj,
        'page_obj': page_obj,
        'staff_stats': staff_stats,
        'search_query': search_query,
        'selected_department': department,
        'selected_status': status_filter,
        'department_choices': Staff.DEPARTMENT_CHOICES,
        'position_choices': Staff.POSITION_CHOICES,
    }
    
    return render(request, "staff/dashboard/manage_staff.html", context)

@login_required
@staff_required
def create_staff(request):
    """
    Create a new staff member
    """
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            staff = form.save()
            messages.success(request, f"Staff member {staff.full_name} created successfully!")
            return redirect('manage_staff')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = StaffForm()
    
    context = {
        'form': form,
        'page_title': "Create New Staff Member",
    }
    
    return render(request, "staff/dashboard/create_staff.html", context)

@login_required
@staff_required
def edit_staff_admin(request, staff_id):
    """
    Edit staff member (admin version)
    """
    staff = get_object_or_404(Staff, id=staff_id)
    
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, f"Staff member {staff.full_name} updated successfully!")
            return redirect('manage_staff')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = StaffForm(instance=staff)
    
    context = {
        'form': form,
        'staff': staff,
        'page_title': f"Edit Staff: {staff.full_name}",
    }
    
    return render(request, "staff/dashboard/edit_staff.html", context)

@login_required
@staff_required
def toggle_staff_status(request, staff_id):
    """
    Toggle staff active status
    """
    staff = get_object_or_404(Staff, id=staff_id)
    
    if request.method == 'POST':
        staff.is_active = not staff.is_active
        staff.save()
        
        action = "activated" if staff.is_active else "deactivated"
        messages.success(request, f"Staff member {staff.full_name} has been {action}.")
    
    return redirect('manage_staff')

@login_required
@staff_required
def delete_staff_admin(request, staff_id):
    """
    Delete a staff member
    """
    staff = get_object_or_404(Staff, id=staff_id)
    
    if request.method == 'POST':
        staff_name = staff.full_name
        staff.delete()
        messages.success(request, f"Staff member {staff_name} has been deleted successfully.")
        return redirect('manage_staff')
    
    context = {
        'staff': staff,
    }
    
    return render(request, "staff/dashboard/confirm_delete_staff.html", context)

@login_required
@staff_required
def user_analytics(request):
    """
    User analytics and statistics
    """
    # User registration trends (last 30 days)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    
    user_registrations = CustomUser.objects.filter(
        date_joined__gte=thirty_days_ago
    ).extra({
        'date': "DATE(date_joined)"
    }).values('date').annotate(count=Count('id')).order_by('date')
    
    # User type distribution
    user_type_distribution = CustomUser.objects.values('user_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Active vs inactive users
    active_users = CustomUser.objects.filter(is_active=True).count()
    inactive_users = CustomUser.objects.filter(is_active=False).count()
    
    # Verified vs unverified users
    verified_users = CustomUser.objects.filter(is_verified=True).count()
    unverified_users = CustomUser.objects.filter(is_verified=False).count()
    
    # Recent activity (last 7 days)
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)
    recent_users = CustomUser.objects.filter(
        date_joined__gte=seven_days_ago
    ).count()
    
    context = {
        'user_registrations': list(user_registrations),
        'user_type_distribution': list(user_type_distribution),
        'active_users': active_users,
        'inactive_users': inactive_users,
        'verified_users': verified_users,
        'unverified_users': unverified_users,
        'recent_users': recent_users,
        'total_users': active_users + inactive_users,
    }
    
    return render(request, "staff/dashboard/user_analytics.html", context)

@login_required
@staff_required
def bulk_user_actions(request):
    """
    Handle bulk actions for users
    """
    if request.method == 'POST':
        user_ids = request.POST.getlist('user_ids')
        action = request.POST.get('action')
        
        if not user_ids:
            messages.error(request, "No users selected.")
            return redirect('user_management')
        
        users = CustomUser.objects.filter(id__in=user_ids)
        
        if action == 'activate':
            users.update(is_active=True)
            messages.success(request, f"{len(users)} users activated successfully.")
        elif action == 'deactivate':
            users.update(is_active=False)
            messages.success(request, f"{len(users)} users deactivated successfully.")
        elif action == 'verify':
            users.update(is_verified=True)
            messages.success(request, f"{len(users)} users verified successfully.")
        elif action == 'delete':
            count = users.count()
            users.delete()
            messages.success(request, f"{count} users deleted successfully.")
        else:
            messages.error(request, "Invalid action selected.")
    
    return redirect('user_management')

# API endpoints for AJAX requests
@login_required
@staff_required
def get_user_stats(request):
    """
    API endpoint to get user statistics (for dashboard widgets)
    """
    stats = {
        'total_users': CustomUser.objects.count(),
        'active_users': CustomUser.objects.filter(is_active=True).count(),
        'new_today': CustomUser.objects.filter(
            date_joined__date=timezone.now().date()
        ).count(),
        'pending_verification': CustomUser.objects.filter(is_verified=False).count(),
    }
    
    return JsonResponse(stats)

# Room Gallery Management Views

@login_required
def room_gallery_management(request, room_id):
    """
    View to manage room gallery images
    """
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')
    
    room = get_object_or_404(Room, pk=room_id, hotel=hotel)
    gallery_images = OurRoomsImage.objects.filter(room=room).order_by('-id')
    
    if request.method == "POST":
        # Handle bulk image upload
        bulk_form = BulkRoomGalleryForm(request.POST, request.FILES)
        if bulk_form.is_valid():
            images = request.FILES.getlist('images')
            uploaded_count = 0
            
            for image in images:
                if image.size > 10 * 1024 * 1024:  # 10MB limit
                    messages.warning(request, f"Image '{image.name}' is too large (max 10MB)")
                    continue
                    
                # Create gallery image instance
                gallery_image = OurRoomsImage.objects.create(
                    room=room,
                    image=image
                )
                uploaded_count += 1
            
            if uploaded_count > 0:
                messages.success(request, f"Successfully uploaded {uploaded_count} images!")
            else:
                messages.error(request, "No images were uploaded.")
            
            return redirect('room-gallery-management', room_id=room.id)
    else:
        bulk_form = BulkRoomGalleryForm()
    
    context = {
        'room': room,
        'hotel': hotel,
        'gallery_images': gallery_images,
        'bulk_form': bulk_form,
    }
    return render(request, 'dashboard/room-detail/room-gallery.html', context)

@login_required
def upload_room_image(request, room_id):
    """
    Upload single room image via AJAX
    """
    hotel = get_manager_hotel(request.user)
    if not hotel:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    room = get_object_or_404(Room, pk=room_id, hotel=hotel)
    
    if request.method == "POST":
        form = RoomGalleryForm(request.POST, request.FILES)
        if form.is_valid():
            gallery_image = form.save(commit=False)
            gallery_image.room = room
            gallery_image.save()
            
            return JsonResponse({
                'success': True,
                'image_id': gallery_image.id,
                'image_url': gallery_image.image.url,
                'alt_text': f"Room {room.room_number} image"
            })
        else:
            return JsonResponse({'error': 'Invalid form data'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def delete_room_image(request, room_id, image_id):
    """
    Delete a room gallery image
    """
    hotel = get_manager_hotel(request.user)
    if not hotel:
        messages.error(request, "You are not registered as a hotel manager")
        return redirect('home')
    
    room = get_object_or_404(Room, pk=room_id, hotel=hotel)
    image = get_object_or_404(OurRoomsImage, pk=image_id, room=room)
    
    if request.method == "POST":
        try:
            # For Cloudinary images, try to delete from cloud storage
            if image.image:
                try:
                    if hasattr(image.image, 'public_id') and image.image.public_id:
                        # Delete from Cloudinary using the public_id
                        cloudinary.uploader.destroy(image.image.public_id)
                    else:
                        # If no public_id, try to extract it from the URL or just skip cloud deletion
                        print(f"Warning: No public_id found for image {image.id}")
                except Exception as cloud_error:
                    print(f"Warning: Could not delete from cloud storage: {cloud_error}")
                    # Continue with database deletion even if cloud deletion fails
            
            # Delete the database record
            image.delete()
            
            messages.success(request, "Image deleted successfully!")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
                
        except Exception as e:
            messages.error(request, f"Error deleting image: {str(e)}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': str(e)}, status=500)
    
    return redirect('room-gallery-management', room_id=room.id)

