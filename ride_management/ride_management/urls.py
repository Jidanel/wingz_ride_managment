from django.contrib import admin
from django.urls import path, include
from rides.views import RideListView 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/rides/', include('rides.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('', RideListView.as_view(), name='home'),
    path("users/", include("users.urls")),
]
