from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.register_user, name='register'),
    path('profile/', views.user_profile, name='profile'),
    path('become-seller/', views.create_seller_profile, name='become-seller'),
    path('become-owner/', views.create_owner_profile, name='become-owner'),
    path('change-password/', views.change_password, name='change-password'),
    ]
