from django.urls import path
from . import views

urlpatterns = [
    path('sign_up/', views.sign_up, name='sign-up'),
    path('login/', views.login_user, name='login'),
    path('logout_user/', views.logout_user, name='logout'),
    path('profile/', views.profile, name='profile'),
]
