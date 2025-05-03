from django.urls import path, include
from .views import SearchAPIView

urlpatterns = [
    path('search/', SearchAPIView.as_view(), name='search-api'),
]
