from django.urls import path, include
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('api/', SearchAPIView.as_view(), name='search-api'),
    path('search/', search_page, name='search-page'),
    path('register/', register_page, name='register-page'),
    path('login/', login_page, name='login-page'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/users/', UserListView.as_view(), name='user-list'), # List all users (admin only)
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Token generation (Login)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Token refresh (Refresh token for new access token)
]
