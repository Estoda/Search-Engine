from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Search API",
        default_version='v1',   
        description="API for searching and managing search results",            
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="programmer82253@gmail.com"),
        license=openapi.License(name="BSD License"),
    )
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('search_app.urls')),

    # Swagger and Redoc URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
