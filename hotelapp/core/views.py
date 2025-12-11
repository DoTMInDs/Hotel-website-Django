from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ValidationError
import uuid
import logging
from django.conf import settings
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime

from .models import Room,Rating,Hotel,Reservation,Booking,Guest,OurRoomsImage
from account.forms import LeadForm,ReservationForm,BookingForm
from .payment_service import PaymentService
from .validators import BookingValidator, ContactValidator, FormValidator

logger = logging.getLogger(__name__)

# Create your views here.

def offline(request):
    """Offline page for PWA"""
    return render(request, 'core/offline.html')

def send_hotel_booking_notification(booking, hotel=None):
    """
    Send email notification to hotel about new booking
    """
    # If hotel is not provided, try to get it from the booking
    if hotel is None:
        hotel = booking.room.hotel
        logger.info(f"Extracted hotel from booking: {hotel.name}")
    
    logger.info(f"Sending hotel notification for booking {booking.id} to {hotel.email}")
    
    subject = f"New Booking Notification - {hotel.name}"
    
    context = {
        'hotel': hotel,
        'booking': booking,
        'room': booking.room,
        'guest': booking.guest,
        'booking_date': booking.created_at,
        'nights': (booking.check_out_date - booking.check_in_date).days,
    }
    
    try:
        html_message = render_to_string('emails/hotel_booking_notification.html', context)
        plain_message = strip_tags(html_message)
        
        from_email = settings.DEFAULT_FROM_EMAIL
        
        send_mail(
            subject,
            plain_message,
            from_email,
            [hotel.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Hotel notification sent successfully to {hotel.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send hotel notification email: {str(e)}")
        return False

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
            lead = form.save()

            # Compose email settings and content
            domain = getattr(settings, 'DOMAIN', request.get_host())
            site_name = getattr(settings, 'SITE_NAME', 'Our Hotel')
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@%s' % request.get_host())
            # contact_recipient = getattr(settings, 'CONTACT_EMAIL', from_email)

            # ---- Confirmation email to user ----
            try:
                subject_user = f"Thanks for contacting {site_name}"
                html_user = render_to_string('emails/contact_confirmation.html', {
                    'lead': lead,
                    'site_name': site_name,
                    'domain': domain,
                })
                plain_user = strip_tags(html_user)
                send_mail(
                    subject_user,
                    plain_user,
                    from_email,
                    [lead.email],
                    html_message=html_user,
                    fail_silently=False,
                )
            except Exception as e:
                logger.warning(f"Failed to send contact confirmation email to user: {e}")

            messages.success(request, 'Your message has been sent successfully! You will receive a confirmation email shortly.')
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

    # --- Filters ---
    name_query = request.GET.get('search', '')
    location_query = request.GET.get('loc-search', '')
    status_query = request.GET.get('status', '')
    rating_query = request.GET.get('rating', '')
    room_type_query = request.GET.get('room_type', '')

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

    # --- Booking (POST) ---
    if request.method == "POST":
        room_id = request.POST.get("room_id")
        check_in = request.POST.get("check_in_date")
        check_out = request.POST.get("check_out_date")
        message = request.POST.get("message", "")

        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to make a booking.")
            return redirect("login")

        if not all([room_id, check_in, check_out]):
            messages.error(request, "Please fill all required fields.")
            return redirect("room-list", pk=hotel.pk)

        room = get_object_or_404(Room, id=room_id)

        # Convert dates
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
        except:
            messages.error(request, "Invalid date format.")
            return redirect("room-list", pk=hotel.pk)

        # Validate date range
        if check_out_date <= check_in_date:
            messages.error(request, "Check-out must be after check-in.")
            return redirect("room-list", pk=hotel.pk)

        # Create or retrieve Guest profile
        guest, created = Guest.objects.get_or_create(
            user=request.user,
            defaults={
                "first_name": request.user.first_name or "Guest",
                "last_name": request.user.last_name or "User",
                "email": request.user.email
            }
        )

        # Create booking (unpaid initially)
        booking = Booking.objects.create(
            guest=guest,
            room=room,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            message=message
        )

        # Total price
        nights = (check_out_date - check_in_date).days
        total_price = nights * room.price
        booking.total_price = total_price

        # Generate Paystack reference
        reference = f"BOOK_{booking.id}_{uuid.uuid4().hex[:8].upper()}"
        booking.paystack_reference = reference
        booking.save()

        # --- Paystack Split Payments ---
        hotel_subaccount = None
        if hasattr(hotel, "paystack_subaccount") and hotel.paystack_subaccount.is_active:
            hotel_subaccount = hotel.paystack_subaccount.subaccount_code

        # Metadata for Paystack dashboard
        metadata = {
            "booking_id": booking.id,
            "room_number": room.room_number,
            "hotel_name": hotel.name,
            "guest_name": f"{guest.first_name} {guest.last_name}",
            "check_in": str(check_in_date),
            "check_out": str(check_out_date),
            "nights": nights,
        }

        # Payment callback URL
        callback_url = request.build_absolute_uri(reverse("verify_booking_payment"))

        # Initialize Paystack Payment
        try:
            payment_response = PaymentService.initialize_payment(
                email=guest.email,
                amount=float(total_price),
                reference=reference,
                callback_url=callback_url,
                metadata=metadata,
                hotel_subaccount=hotel_subaccount,
            )

            if payment_response.get("status"):
                # Save access code
                booking.paystack_access_code = payment_response["data"]["access_code"]
                booking.save()

                # Redirect user to Paystack
                return redirect(payment_response["data"]["authorization_url"])

            else:
                messages.error(request, "Payment could not be initialized.")
                booking.delete()
                return redirect("room-list", pk=hotel.pk)

        except Exception as e:
            messages.error(request, "Payment service unavailable.")
            booking.delete()
            return redirect("room-list", pk=hotel.pk)

    # Paginate rooms
    paginator = Paginator(rooms, 10)
    page_number = request.GET.get("page")

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Render
    context = {
        "hotel": hotel,
        "rooms": page_obj,
        "page_obj": page_obj,
        "status_choices": Room.ROOM_STATUS_CHOICES,
        "rating_choices": Rating.objects.all(),
        "room_type_choices": Room.BED_TYPE_CHOICES,
        "name_query": name_query,
        "location_query": location_query,
        "status_query": status_query,
        "rating_query": rating_query,
        "room_type_query": room_type_query,
    }

    return render(request, "core/room_list.html", context)

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
    # Get additional gallery images for this room
    gallery_images = OurRoomsImage.objects.filter(room=room)
    
    if request.method == 'POST':
        try:
            # Validate required fields
            required_fields = ['room_id', 'check_in_date', 'check_out_date', 'email', 'first_name', 'last_name']
            FormValidator.validate_required_fields(request.POST, required_fields)
            
            room_id = request.POST.get('room_id')
            check_in_date = request.POST.get('check_in_date')
            check_out_date = request.POST.get('check_out_date')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone_number = request.POST.get('phone_number', '')
            address = request.POST.get('address', '')
            message = request.POST.get('message', '')
            
            # Validate email
            ContactValidator.validate_email(email)
            
            # Get room and validate
            booking_room = get_object_or_404(Room, id=room_id)
            
            # Check if room is available
            if booking_room.status != 'Available':
                messages.error(request, "This room is not available for booking.")
                return redirect('room-detail', pk=pk)
            
            # Parse and validate dates
            try:
                check_in = datetime.strptime(check_in_date, "%Y-%m-%d").date()
                check_out = datetime.strptime(check_out_date, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format. Please use the date picker.")
                return redirect('room-detail', pk=pk)
            
            # Validate dates using validator
            BookingValidator.validate_dates(check_in, check_out)
            
            # Calculate total price
            nights = (check_out - check_in).days
            total_price = booking_room.price * nights
            
            # Validate payment amount
            BookingValidator.validate_payment_amount(total_price)
            
            # Get or create guest profile
            if request.user.is_authenticated:
                guest, created = Guest.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'first_name': first_name or request.user.first_name,
                        'last_name': last_name or request.user.last_name,
                        'email': email or request.user.email,
                        'phone_number': phone_number,
                        'address': address
                    }
                )
                # Update guest info if provided
                if first_name:
                    guest.first_name = first_name
                if last_name:
                    guest.last_name = last_name
                if email:
                    guest.email = email
                if phone_number:
                    guest.phone_number = phone_number
                if address:
                    guest.address = address
                guest.save()
            else:
                messages.error(request, "You must be logged in to make a booking.")
                return redirect('login')
            
            # Create booking with Paystack reference
            booking = Booking.objects.create(
                guest=guest,
                room=booking_room,
                check_in_date=check_in,
                check_out_date=check_out,
                message=message,
                total_price=total_price,
                is_paid=False
            )
            
            # Generate unique reference for Paystack payment
            reference = f"ROOM_{booking_room.id}_{booking.id}_{uuid.uuid4().hex[:8].upper()}"
            booking.paystack_reference = reference
            booking.save()
            
            # Get hotel subaccount if exists (for split payments)
            hotel = booking_room.hotel
            hotel_subaccount = getattr(hotel, 'paystack_subaccount_code', None) if hotel else None
            
            # Prepare metadata for Paystack
            metadata = {
                "booking_id": booking.id,
                "room_number": booking_room.room_number,
                "hotel_name": hotel.name if hotel else "Unknown Hotel",
                "guest_name": f"{first_name} {last_name}",
                "check_in": check_in.strftime("%Y-%m-%d"),
                "check_out": check_out.strftime("%Y-%m-%d"),
                "nights": nights
            }
            
            # Initialize payment using PaymentService (Paystack)
            callback_url = request.build_absolute_uri(reverse('verify_booking_payment'))
            
            try:
                payment_response = PaymentService.initialize_payment(
                    email=email,
                    amount=float(total_price),
                    reference=reference,
                    callback_url=callback_url,
                    metadata=metadata,
                    hotel_subaccount=hotel_subaccount
                )
                
                if payment_response.get("status"):
                    # Save access code and redirect to Paystack payment page
                    booking.paystack_access_code = payment_response["data"]["access_code"]
                    booking.save()
                    return redirect(payment_response["data"]["authorization_url"])
                else:
                    messages.error(request, f"Payment could not be initialized: {payment_response.get('message')}")
                    booking.delete()  # Clean up failed booking
                    
            except Exception as e:
                logger.error(f"Payment initialization error: {str(e)}")
                messages.error(request, "Payment service is currently unavailable. Please try again later.")
                booking.delete()  # Clean up failed booking
                
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Booking error in room detail: {str(e)}")
            messages.error(request, "An error occurred while processing your booking. Please try again.")
    
    context = {
        'room': room,
        'gallery_images': gallery_images,
        'PAYSTACK_PUBLIC_KEY': settings.PAYSTACK_PUBLIC_KEY
    }
    return render(request, 'detail/room_detail.html', context)

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, guest__user=request.user)
    if request.method == 'POST':
        try:
            booking.delete()
            return redirect(f'{reverse("my_booking")}?delete_status=success&delete_message=Booking deleted successfully!')
        except Exception as e:
            logger.error(f"Error deleting booking: {str(e)}")
            return redirect(f'{reverse("my_booking")}?delete_status=error&delete_message=Failed to delete booking. Please try again.')
    return redirect('my_booking')


# payment for booking using hubtel with split payments
def create_booking_and_pay(request):
    if request.method == 'POST':
        try:
            # Get form data
            room_id = request.POST.get('room_id')
            check_in_str = request.POST.get('check_in_date')
            check_out_str = request.POST.get('check_out_date')
            message = request.POST.get('message', '')
            
            # Validate required fields
            if not all([room_id, check_in_str, check_out_str]):
                messages.error(request, "Please fill all required fields.")
                return redirect('hotel-rooms')
            
            # Parse dates
            try:
                check_in_date = datetime.strptime(check_in_str, "%Y-%m-%d").date()
                check_out_date = datetime.strptime(check_out_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format.")
                return redirect('hotel-rooms')
            
            # Get room
            room = get_object_or_404(Room, id=room_id)
            hotel = room.hotel
            
            # Get or create guest
            guest, created = Guest.objects.get_or_create(
                user=request.user,
                defaults={
                    'first_name': request.user.first_name or 'Guest',
                    'last_name': request.user.last_name or 'User',
                    'email': request.user.email
                }
            )
            
            # Update guest info if they provided it
            if 'first_name' in request.POST and request.POST['first_name']:
                guest.first_name = request.POST['first_name']
            if 'last_name' in request.POST and request.POST['last_name']:
                guest.last_name = request.POST['last_name']
            if 'email' in request.POST and request.POST['email']:
                guest.email = request.POST['email']
            if 'phone_number' in request.POST:
                guest.phone_number = request.POST['phone_number']
            
            guest.save()
            
            # Create booking
            booking = Booking.objects.create(
                guest=guest,
                room=room,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                message=message,
                total_price=0,  # Will be calculated
                is_paid=False
            )
            
            # Calculate total price
            booking.total_price = booking.calculate_total_price()
            
            # Generate Paystack reference
            reference = f"BOOK_{booking.id}_{uuid.uuid4().hex[:8].upper()}"
            booking.paystack_reference = reference
            booking.save()
            
            # Get hotel subaccount for split payment (using your model structure)
            hotel_subaccount = None
            commission_percentage = 15.00  # Default platform commission
            
            # Check if hotel has payment setup
            if hasattr(hotel, 'paystack_subaccount') and hotel.paystack_subaccount.is_active:
                hotel_subaccount = hotel.paystack_subaccount.subaccount_code
                commission_percentage = float(hotel.paystack_subaccount.percentage_charge)
            elif hasattr(hotel, 'is_payment_active') and hotel.is_payment_active and hotel.paystack_subaccount_code:
                # If using integrated fields approach
                hotel_subaccount = hotel.paystack_subaccount_code
                commission_percentage = float(hotel.platform_commission)
            
            # Prepare metadata
            metadata = {
                "booking_id": booking.id,
                "room_id": room.id,
                "room_number": room.room_number,
                "hotel_id": hotel.id,
                "hotel_name": hotel.name,
                "guest_id": guest.id,
                "guest_name": f"{guest.first_name} {guest.last_name}",
                "check_in": check_in_date.strftime("%Y-%m-%d"),
                "check_out": check_out_date.strftime("%Y-%m-%d"),
                "nights": (check_out_date - check_in_date).days,
                "split_payment": bool(hotel_subaccount),
                "commission_percentage": commission_percentage,
                "platform_fee": float(booking.total_price) * (commission_percentage / 100),
                "hotel_amount": float(booking.total_price) * ((100 - commission_percentage) / 100)
            }
            
            # Build callback URL
            callback_url = request.build_absolute_uri(reverse('verify_booking_payment'))
            
            # Initialize payment
            payment_response = PaymentService.initialize_payment(
                email=guest.email,  # Use guest's email from your Guest model
                amount=float(booking.total_price),
                reference=reference,
                callback_url=callback_url,
                metadata=metadata,
                hotel_subaccount=hotel_subaccount  # This enables split payment
            )
            
            if payment_response.get("status"):
                # Save access code
                booking.paystack_access_code = payment_response["data"]["access_code"]
                booking.save()
                
                # Redirect to Paystack payment page
                return redirect(payment_response["data"]["authorization_url"])
            else:
                error_msg = payment_response.get("message", "Payment initialization failed")
                messages.error(request, f"Payment Error: {error_msg}")
                booking.delete()
                return redirect('room-list', pk=hotel.pk)
                
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Booking error: {str(e)}")
            messages.error(request, "An error occurred. Please try again.")
    
    return redirect('hotel-rooms')
    
def verify_booking_payment(request):
    reference = request.GET.get('reference')
    
    if not reference:
        messages.error(request, "No payment reference provided.")
        return redirect('booking-payment-failure')
    
    try:
        # Verify payment with Paystack
        payment_data = PaymentService.verify_payment(reference)
        
        if payment_data.get("status"):
            payment_info = payment_data.get("data", {})
            
            if payment_info.get("status") == "success":
                # Find booking
                booking = Booking.objects.filter(paystack_reference=reference).first()
                
                if booking and not booking.is_paid:
                    # Mark as paid
                    booking.is_paid = True
                    booking.save()
                    
                    # Create reservation from booking
                    try:
                        reservation = Reservation.create_from_booking(booking)
                        logger.info(f"Reservation {reservation.id} created from booking {booking.id}")
                    except Exception as e:
                        logger.error(f"Failed to create reservation: {str(e)}")
                        messages.warning(request, "Booking confirmed but reservation creation failed.")
                    
                    # Send confirmation email to guest
                    try:
                        subject = f"Booking Confirmation - {booking.room.hotel.name}"
                        html_message = render_to_string('emails/booking_confirmation.html', {
                            'booking': booking,
                            'guest': booking.guest,
                            'hotel': booking.room.hotel,
                            'room': booking.room,
                            'check_in': booking.check_in_date,
                            'check_out': booking.check_out_date,
                        })
                        
                        send_mail(
                            subject=subject,
                            message='',  # Plain text version
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[booking.guest.email],
                            html_message=html_message,
                            fail_silently=False,
                        )
                    except Exception as e:
                        logger.error(f"Email send failed: {str(e)}")
                    
                    # Send notification to hotel
                    try:
                        send_hotel_booking_notification(booking, booking.room.hotel)
                    except Exception as e:
                        logger.error(f"Hotel notification failed: {str(e)}")
                    
                    # Success page
                    return redirect(f'{reverse("booking-payment-success")}?booking_id={booking.id}')
                else:
                    messages.warning(request, "Payment already processed.")
                    return redirect('booking-payment-success')
            else:
                messages.error(request, f"Payment failed: {payment_info.get('gateway_response', 'Unknown error')}")
        else:
            messages.error(request, "Payment verification failed.")
            
    except Exception as e:
        logger.error(f"Payment verification error: {str(e)}")
        messages.error(request, "Error verifying payment.")
    
    return redirect('booking-payment-failure')

def send_hotel_booking_notification(booking, hotel):
    """Send email notification to hotel about new booking"""
    try:
        subject = f"New Booking - {hotel.name}"
        
        # Calculate amounts for split payment
        total_amount = booking.total_price
        metadata = booking.paystack_reference.metadata if hasattr(booking.paystack_reference, 'metadata') else {}
        
        if metadata.get('split_payment'):
            commission = metadata.get('commission_percentage', 15.00)
            platform_fee = float(total_amount) * (commission / 100)
            hotel_amount = float(total_amount) * ((100 - commission) / 100)
        else:
            platform_fee = float(total_amount)
            hotel_amount = 0.00
        
        html_message = render_to_string('emails/hotel_booking_notification.html', {
            'hotel': hotel,
            'booking': booking,
            'guest': booking.guest,
            'room': booking.room,
            'check_in': booking.check_in_date,
            'check_out': booking.check_out_date,
            'total_amount': total_amount,
            'hotel_amount': hotel_amount,
            'platform_fee': platform_fee,
            'split_payment': metadata.get('split_payment', False),
            'commission_percentage': metadata.get('commission_percentage', 15.00),
        })
        
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[hotel.email],
            html_message=html_message,
            fail_silently=True,
        )
        
        return True
    except Exception as e:
        logger.error(f"Hotel notification error: {str(e)}")
        return False

def booking_success(request):
    booking_id = request.GET.get('booking_id')
    booking = None
    
    if booking_id:
        try:
            booking = Booking.objects.get(id=booking_id, is_paid=True)
        except Booking.DoesNotExist:
            pass
    
    context = {
        'booking': booking
    }
    return render(request, 'payments/success.html', context)

def booking_failure(request):
    return render(request, 'payments/failure.html')


