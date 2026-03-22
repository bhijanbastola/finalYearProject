
from django.urls import path
from . import views

app_name = 'maps'

urlpatterns = [
    # Main map view
    path('', views.MapView.as_view(), name='map_view'),
    path('api/locations/', views.get_all_locations, name='get_all_locations'),
    path('api/all-locations-list/', views.get_all_attractions_and_stations, name='all_locations_list'),
    path('api/search-location/', views.search_location_by_name, name='search_location'),
    path('api/calculate-route-with-roads/', views.calculate_route_with_roads, name='calculate_route_with_roads'),
]
