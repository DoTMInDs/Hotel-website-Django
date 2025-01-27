from django.contrib import admin
from .models import Rating,OurRooms,HotelPost,Lead


# Register your models here.
admin.site.register(Rating)
admin.site.register(OurRooms)
admin.site.register(HotelPost)
admin.site.register(Lead)