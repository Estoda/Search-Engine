from django.urls import path, include
from .views import *

urlpatterns = [
    path('search/', SearchAPIView.as_view(), name='search-api'),
    path('', search_page, name='search-page'),
]
