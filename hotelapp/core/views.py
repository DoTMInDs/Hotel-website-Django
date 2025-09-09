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

from .models import Room,Rating,Hotel,Reservation,Booking,Guest
from account.forms import LeadForm,ReservationForm,BookingForm
from .payment_service import PaymentService
from .validators import BookingValidator, ContactValidator, FormValidator

logger = logging.getLogger(__name__)

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
            lead = form.save()

            # Compose email settings and content
            domain = getattr(settings, 'DOMAIN', request.get_host())
            site_name = getattr(settings, 'SITE_NAME', 'Our Hotel')
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@%s' % request.get_host())
            contact_recipient = getattr(settings, 'CONTACT_EMAIL', from_email)

            # ---- Notify site / reservations team ----
            try:
                subject_admin = f"New contact request from {lead.full_name}"
                html_admin = render_to_string('emails/contact_notification.html', {
                    'lead': lead,
                    'site_name': site_name,
                    'domain': domain,
                })
                plain_admin = strip_tags(html_admin)
                send_mail(
                    subject_admin,
                    plain_admin,
                    from_email,
                    [contact_recipient],
                    html_message=html_admin,
                    fail_silently=False,
                )
            except Exception as e:
                logger.warning(f"Failed to send contact notification email: {e}")

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
        try:
            booking.delete()
            return redirect(f'{reverse("my_booking")}?delete_status=success&delete_message=Booking deleted successfully!')
        except Exception as e:
            logger.error(f"Error deleting booking: {str(e)}")
            return redirect(f'{reverse("my_booking")}?delete_status=error&delete_message=Failed to delete booking. Please try again.')
    return redirect('my_booking')



# payment for booking using paystack
def create_booking_and_pay(request):
    if request.method == 'POST':
        try:
            # Validate required fields
            required_fields = ['room_id', 'check_in_date', 'check_out_date', 'email']
            FormValidator.validate_required_fields(request.POST, required_fields)
            
            room_id = request.POST.get('room_id')
            check_in_date = request.POST.get('check_in_date')
            check_out_date = request.POST.get('check_out_date')
            email = request.POST.get('email')
            
            # Validate email
            ContactValidator.validate_email(email)
            
            # Get room and validate
            room = get_object_or_404(Room, id=room_id)
            
            # Parse and validate dates
            try:
                check_in = datetime.strptime(check_in_date, "%Y-%m-%d").date()
                check_out = datetime.strptime(check_out_date, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD format.")
                return redirect('room-list', pk=room.hotel.pk)
            
            # Validate dates using validator
            BookingValidator.validate_dates(check_in, check_out)
            
            # Validate payment amount
            total_price = room.price * (check_out - check_in).days
            BookingValidator.validate_payment_amount(total_price)
            
            # Create booking
            booking = Booking.objects.create(
                guest=request.user.guest_profile,
                room=room,
                check_in_date=check_in,
                check_out_date=check_out,
                message=request.POST.get('message', ''),
                total_price=0
            )
            
            # Calculate total price
            booking.total_price = booking.calculate_total_price()
            booking.save()
            
            # Generate reference
            reference = str(uuid.uuid4())
            booking.paystack_reference = reference
            booking.save()
            
            # Initialize payment using service
            callback_url = request.build_absolute_uri(reverse('verify_booking_payment'))
            payment_response = PaymentService.initialize_payment(
                email=email,
                amount=float(booking.total_price),
                reference=reference,
                callback_url=callback_url
            )
            
            if payment_response.get("status"):
                return redirect(payment_response["data"]["authorization_url"])
            else:
                messages.error(request, "Payment could not be initialized. Please try again.")
                booking.delete()  # Clean up failed booking
                
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Payment initialization error: {str(e)}")
            messages.error(request, "An error occurred while processing your payment. Please try again.")
        
        # Fallback redirect
        return redirect('hotel-rooms')
    
def verify_booking_payment(request):
    reference = request.GET.get('reference')
    
    if not reference:
        messages.error(request, "Invalid payment reference.")
        return redirect('booking-payment-failure')
    
    try:
        # Verify payment using service
        payment_data = PaymentService.verify_payment(reference)
        
        if payment_data.get("status") and payment_data["data"]["status"] == "success":
            booking = Booking.objects.filter(paystack_reference=reference).first()
            
            if booking and not booking.is_paid:
                booking.is_paid = True
                booking.save()

                # Send confirmation email
                try:
                    subject = "Booking Confirmation - Payment Successful"
                    message = render_to_string("emails/booking_confirmation.html", {
                        'booking': booking,
                        'guest': booking.guest,
                    })
                    send_mail(
                        subject,
                        '',
                        settings.DEFAULT_FROM_EMAIL,
                        [booking.guest.email],
                        html_message=message,
                        fail_silently=True
                    )
                except Exception as e:
                    logger.error(f"Failed to send confirmation email: {str(e)}")
                
                # Redirect to success page with booking data
                return redirect(f'{reverse("booking-payment-success")}?booking_id={booking.id}')
            else:
                messages.warning(request, "Payment already processed or booking not found.")
                return redirect('booking-payment-success')
        else:
            messages.error(request, "Payment verification failed.")
            return redirect('booking-payment-failure')
            
    except ValidationError as e:
        messages.error(request, str(e))
        return redirect('booking-payment-failure')
    except Exception as e:
        logger.error(f"Payment verification error: {str(e)}")
        messages.error(request, "An error occurred while verifying your payment.")
        return redirect('booking-payment-failure')

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