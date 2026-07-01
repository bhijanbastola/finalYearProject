# maps/urls.py
# CORRECT VERSION with locations-near endpoint

from django.urls import path
from . import views

app_name = 'maps'

urlpatterns = [
    # Main map view
    path('', views.MapView.as_view(), name='map_view'),
    
    # API endpoints
    path('api/locations/', views.get_all_locations, name='get_all_locations'),
    path('api/locations-near/', views.get_attractions_and_stations_by_location, name='locations_near'),
    path('api/search-location/', views.search_location_by_name, name='search_location'),
    path('api/calculate-route-with-roads/', views.calculate_route_with_roads, name='calculate_route_with_roads'),

    path('add/', views.add_location_menu, name='add_location_menu'),
    path('add/attraction/', views.add_attraction, name='add_attraction'),
    path('add/attraction/success/<int:attraction_id>/', views.add_attraction_success, name='add_attraction_success'),
    path('add/ev-station/', views.add_ev_station, name='add_ev_station'),
    path('add/ev-station/success/<int:station_id>/', views.add_ev_station_success, name='add_ev_station_success'),
]