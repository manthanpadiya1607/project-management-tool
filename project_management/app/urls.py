from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserProfileView, UserPasswordResetView,SendPasswordResetEmailView, UserPasswordChangeView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login', UserLoginView.as_view(), name= 'login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('reset-password/', UserPasswordResetView.as_view(), name='reset-password'),
    path('reset-password-email/', SendPasswordResetEmailView.as_view(), name='reset-password-email'),
    path('password-reset/<str:uid>/<token>/', UserPasswordChangeView.as_view(), name= 'password-change' )

]