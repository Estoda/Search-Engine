from django.urls import path, include
from .views import *

urlpatterns = [
    path('api/', SearchAPIView.as_view(), name='search-api'),
    path('search/', search_page, name='search-page'),
]
