from django.contrib import admin
from .models import Rating,OurRoom,HotelPost,Lead,Manager
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

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
    
class OurRoomAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'star_rating')
    
class HotelPostAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'dated_on')
    
# Register your models here.
admin.site.register(Rating)
admin.site.register(OurRoom,OurRoomAdmin)
admin.site.register(HotelPost,HotelPostAdmin)
admin.site.register(Lead,LeadAdmin)
admin.site.unregister(User)
admin.site.register(User,UserAdmin)