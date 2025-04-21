# from django.utils import timezone
# from .models import Reservation, Room
# from datetime import timedelta

# def is_room_available(room_id, check_in, check_out, reservation_id=None):
#     """
#     Check if a room is available between given dates
#     - reservation_id is optional, used when updating an existing reservation
#     """
#     try:
#         room = Room.objects.get(id=room_id)
#         if room.status != 'A':  # Not Available
#             return False
#     except Room.DoesNotExist:
#         return False
    
#     # Get all conflicting reservations (excluding the current one if updating)
#     conflicts = Reservation.objects.filter(
#         room_id=room_id,
#         check_out__gt=check_in,
#         check_in__lt=check_out,
#         status__in=['C', 'I']  # Confirmed or Checked-in
#     ).exclude(id=reservation_id)  # Exclude current reservation if updating
    
#     return not conflicts.exists()

# def get_available_rooms(check_in, check_out, room_type=None):
#     """
#     Get all available rooms between given dates, optionally filtered by type
#     """
#     # Get all rooms that are marked as available
#     rooms = Room.objects.filter(status='A')
    
#     if room_type:
#         rooms = rooms.filter(room_type=room_type)
    
#     available_rooms = []
#     for room in rooms:
#         if is_room_available(room.id, check_in, check_out):
#             available_rooms.append(room)
    
#     return available_rooms