from dj_rest_auth.jwt_auth import get_refresh_view
from django.urls import path

from .views import (CookieBasedLogoutView, CookieBasedRegisterView,
                    CustomLoginView)

app_name = 'user_account'

urlpatterns = [
    path('register/', CookieBasedRegisterView.as_view(), name='auth-register'),
    path('login/', CustomLoginView.as_view(), name='auth-login'),
    path('logout/', CookieBasedLogoutView.as_view(), name='auth-logout'),
    path('refresh/', get_refresh_view().as_view(), name='token_refresh'),
]