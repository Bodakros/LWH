from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    # User profile
    path('profile/', views.user_profile, name='profile'),
    path('change-password/', views.change_password, name='change-password'),

    # Seller account
    path('seller/create/', views.create_seller_account, name='create-seller-account'),
    path('seller/', views.seller_account_detail, name='seller-account-detail'),

    # Owner account
    path('owner/create/', views.create_owner_account, name='create-owner-account'),
    path('owner/', views.owner_account_detail, name='owner-account-detail'),

    # Session management
    path('switch-account/', views.switch_account, name='switch-account'),
    path('current-session/', views.current_session, name='current-session'),
]