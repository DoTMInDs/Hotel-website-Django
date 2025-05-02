from django.contrib import admin
from .models import Rating,Room,Hotel,Lead,Manager,Staff,Amenity,OurRoomsImage,Reservation,Guest,Booking
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _ 
from django.urls import reverse
from django.utils.html import format_html

class ManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'hotel_post', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone', 'hotel_post__name')
    raw_id_fields = ('user', 'hotel_post') # Use raw_id_fields
    readonly_fields = ('created_at', 'updated_at')

    # Custom display for the linked User
    def user_display(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_display.short_description = _("User")
    
class ManagerInline(admin.StackedInline):
    model=Manager
    can_delete=False
    fields = ('phone', 'hotel_post', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
class UserAdmin(BaseUserAdmin):
    inlines=[ManagerInline]
class LeadAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('full_name', 'email')
    readonly_fields = ('created_at',)
    
class GuestAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'email', 'phone_number', 'user_link', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'user__username')
    ordering = ('last_name', 'first_name',)
    raw_id_fields = ('user',) # Use raw_id_fields for foreign key to User if many users
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone_number', 'address')
        }),
         (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # Custom column to link to the User object
    def user_link(self, obj):
        if obj.user:
            url = reverse("admin:auth_user_change", args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "-"
    user_link.short_description = _("User Account")
    
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'hotel', 'room_type', 'status', 'bed_type', 'view_reservations_link')
    list_filter = ('hotel', 'room_type', 'status', 'bed_type')
    search_fields = ('room_number', 'hotel__name', 'room_type__name')
    ordering = ('hotel__name', 'room_number',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('hotel', 'room_number', 'room_type', 'price_per_night_override', 'status', 'bed_type', 'description', 'amenities')
        }),
         (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    filter_horizontal = ('amenities',)

    # Custom column to link to reservations for this room
    def view_reservations_link(self, obj):
        # Construct the URL for the Reservation admin list filtered by this room
        url = (
            reverse("admin:%s_%s_changelist" % (obj._meta.app_label, "reservation"))
            + f"?room__id={obj.id}"
        )
        return format_html('<a href="{}">View Reservations ({})</a>', url, obj.reservations.count()) # Count related reservations

    view_reservations_link.short_description = _("Reservations")
    
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'phone_number', 'email', 'created_at')
    list_filter = ('region',)
    search_fields = ('name', 'location', 'phone_number', 'email')
    ordering = ('name',)
    readonly_fields = ('created_at',) # Assuming dated_on was renamed to created_at
    fieldsets = (
        (None, {
            'fields': ('name', 'phone_number', 'email', 'location', 'region', 'logo', 'description', 'amenities')
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
            'classes': ('collapse',), # Hide by default
        }),
    )
    filter_horizontal = ('amenities',) 
    
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'id','check_in_date', 'check_out_date',
        'status', 'num_adults', 'num_children', 'num_guests', 'total_price', 'booking_source'
    )
   

# Register your models here.
admin.site.register(Rating)
admin.site.register(Room,RoomAdmin)
admin.site.register(Hotel,HotelAdmin)
admin.site.register(Lead,LeadAdmin)
admin.site.unregister(User)
admin.site.register(Manager,ManagerAdmin)
admin.site.register(Reservation,ReservationAdmin)
admin.site.register(Guest)
admin.site.register(Booking)
admin.site.register(Amenity)
admin.site.register(OurRoomsImage)
admin.site.register(User,UserAdmin)
admin.site.register(Staff)