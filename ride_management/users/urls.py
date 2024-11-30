from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # Si vous avez des vues personnalisées

urlpatterns = [
    # Login
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),

    # Logout
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Register
    path('register/', views.register, name='register'),

    # Mot de passe oublié
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
]
