# maps/views.py
# CORRECT VERSION - Dropdowns show attractions/EV of selected place, clickable map

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.db.models import Q
from .models import TouristAttraction, EVChargingStation, Route, Waypoint
import json
import math
import requests


class MapView(TemplateView):
    """Main map view"""
    template_name = 'maps.html'


def get_attractions_and_stations_by_location(request):
    """
    Get attractions and EV stations near a specific location
    GET /maps/api/locations-near/?lat=27.7&lng=85.3&radius=20
    """
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
        radius = float(request.GET.get('radius', 20))  # Default 20km radius
        
        attractions = []
        ev_stations = []
        
        # Find attractions within radius
        for attr in TouristAttraction.objects.filter(is_active=True):
            distance = haversine_distance(lat, lng, attr.latitude, attr.longitude)
            if distance <= radius:
                attractions.append({
                    'id': attr.id,
                    'name': attr.name,
                    'latitude': attr.latitude,
                    'longitude': attr.longitude,
                    'category': attr.category,
                    'rating': float(attr.rating) if attr.rating else None,
                    'distance': round(distance, 2)
                })
        
        # Find EV stations within radius
        for station in EVChargingStation.objects.filter(is_active=True, is_operational=True):
            distance = haversine_distance(lat, lng, station.latitude, station.longitude)
            if distance <= radius:
                ev_stations.append({
                    'id': station.id,
                    'name': station.name,
                    'latitude': station.latitude,
                    'longitude': station.longitude,
                    'charger_type': station.charger_type,
                    'distance': round(distance, 2)
                })
        
        # Sort by distance
        attractions.sort(key=lambda x: x['distance'])
        ev_stations.sort(key=lambda x: x['distance'])
        
        return JsonResponse({
            'attractions': attractions,
            'ev_stations': ev_stations
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def search_location_by_name(request):
    """Search for places by name"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    results = []
    
    # Search attractions
    attractions = TouristAttraction.objects.filter(
        Q(name__icontains=query) | Q(address__icontains=query),
        is_active=True
    )[:10]
    
    for attr in attractions:
        results.append({
            'id': attr.id,
            'name': attr.name,
            'latitude': attr.latitude,
            'longitude': attr.longitude,
            'type': 'attraction',
            'category': attr.category,
            'address': attr.address or ''
        })
    
    # Search EV stations
    stations = EVChargingStation.objects.filter(
        Q(name__icontains=query) | Q(address__icontains=query),
        is_active=True
    )[:10]
    
    for station in stations:
        results.append({
            'id': station.id,
            'name': station.name,
            'latitude': station.latitude,
            'longitude': station.longitude,
            'type': 'ev_station',
            'charger_type': station.charger_type,
            'address': station.address or ''
        })
    
    # City centers
    city_coords = {
        'kathmandu': {'latitude': 27.7172, 'longitude': 85.3240, 'name': 'Kathmandu'},
        'pokhara': {'latitude': 28.2096, 'longitude': 83.9856, 'name': 'Pokhara'},
        'chitwan': {'latitude': 27.5291, 'longitude': 84.3542, 'name': 'Chitwan'},
        'lumbini': {'latitude': 27.4833, 'longitude': 83.2764, 'name': 'Lumbini'},
        'bhaktapur': {'latitude': 27.6710, 'longitude': 85.4298, 'name': 'Bhaktapur'},
        'patan': {'latitude': 27.6662, 'longitude': 85.3254, 'name': 'Patan'},
    }
    
    for city_key, city_data in city_coords.items():
        if query.lower() in city_key:
            results.insert(0, {
                'id': f'city_{city_key}',
                'name': city_data['name'],
                'latitude': city_data['latitude'],
                'longitude': city_data['longitude'],
                'type': 'city',
                'address': f'{city_data["name"]} City Center'
            })
    
    return JsonResponse({'results': results})


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km"""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return 6371 * c


def get_road_route_with_alternatives(start_lat, start_lng, end_lat, end_lng):
    """Get road routes from OSRM"""
    try:
        coords = f"{start_lng},{start_lat};{end_lng},{end_lat}"
        url = f"http://router.project-osrm.org/route/v1/driving/{coords}"
        params = {
            'overview': 'full',
            'geometries': 'geojson',
            'alternatives': 'true',
            'steps': 'true'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 'Ok' and data.get('routes'):
                return [{
                    'success': True,
                    'coordinates': route['geometry']['coordinates'],
                    'distance': route['distance'] / 1000,
                    'duration': route['duration'] / 60,
                } for route in data['routes']]
        
        return [{
            'success': False,
            'coordinates': [[start_lng, start_lat], [end_lng, end_lat]],
            'distance': haversine_distance(start_lat, start_lng, end_lat, end_lng),
            'duration': 0
        }]
    except Exception as e:
        print(f"OSRM Error: {e}")
        return [{
            'success': False,
            'coordinates': [[start_lng, start_lat], [end_lng, end_lat]],
            'distance': haversine_distance(start_lat, start_lng, end_lat, end_lng),
            'duration': 0
        }]


@csrf_exempt
def calculate_route_with_roads(request):
    """Calculate route with checkbox options"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)
    
    try:
        data = json.loads(request.body)
        
        start_lat = float(data.get('start_lat'))
        start_lng = float(data.get('start_lng'))
        start_name = data.get('start_name', 'Start')
        end_lat = float(data.get('end_lat'))
        end_lng = float(data.get('end_lng'))
        end_name = data.get('end_name', 'End')
        include_attractions = data.get('include_attractions', True)
        include_ev_stations = data.get('include_ev_stations', True)
        
        # Get routes from OSRM
        all_routes = get_road_route_with_alternatives(start_lat, start_lng, end_lat, end_lng)
        
        attractions_list = []
        ev_stations_list = []
        
        # Get all attractions and EV stations in region
        min_lat = min(start_lat, end_lat) - 1.0
        max_lat = max(start_lat, end_lat) + 1.0
        min_lng = min(start_lng, end_lng) - 1.0
        max_lng = max(start_lng, end_lng) + 1.0
        
        if include_attractions:
            attractions_list = list(TouristAttraction.objects.filter(
                is_active=True,
                latitude__gte=min_lat, latitude__lte=max_lat,
                longitude__gte=min_lng, longitude__lte=max_lng
            ))
        
        if include_ev_stations:
            ev_stations_list = list(EVChargingStation.objects.filter(
                is_active=True, is_operational=True,
                latitude__gte=min_lat, latitude__lte=max_lat,
                longitude__gte=min_lng, longitude__lte=max_lng
            ))
        
        # Process each route
        processed_routes = []
        for route_data in all_routes:
            attractions_on_route = []
            ev_on_route = []
            
            # Find stops near this route
            for attr in attractions_list:
                if _is_near_path(attr.latitude, attr.longitude, route_data['coordinates'], 10):
                    attractions_on_route.append({
                        'id': attr.id,
                        'name': attr.name,
                        'latitude': attr.latitude,
                        'longitude': attr.longitude,
                        'type': 'attraction',
                        'category': attr.category
                    })
            
            for station in ev_stations_list:
                if _is_near_path(station.latitude, station.longitude, route_data['coordinates'], 10):
                    ev_on_route.append({
                        'id': station.id,
                        'name': station.name,
                        'latitude': station.latitude,
                        'longitude': station.longitude,
                        'type': 'ev_station',
                        'charger_type': station.charger_type
                    })
            
            route_stops = [{'name': start_name, 'latitude': start_lat, 'longitude': start_lng, 'type': 'start'}]
            route_stops.extend(sorted(attractions_on_route, key=lambda x: haversine_distance(start_lat, start_lng, x['latitude'], x['longitude'])))
            route_stops.extend(sorted(ev_on_route, key=lambda x: haversine_distance(start_lat, start_lng, x['latitude'], x['longitude'])))
            route_stops.append({'name': end_name, 'latitude': end_lat, 'longitude': end_lng, 'type': 'end'})
            
            processed_routes.append({
                'coordinates': route_data['coordinates'],
                'distance': round(route_data['distance'], 2),
                'duration': round(route_data['duration'], 2) if route_data.get('duration') else round((route_data['distance'] / 50) * 60, 2),
                'stops': route_stops,
                'using_roads': route_data['success'],
                'attractions_count': len(attractions_on_route),
                'ev_stations_count': len(ev_on_route)
            })
        
        return JsonResponse({
            'success': True,
            'shortest_route': processed_routes[0] if processed_routes else None,
            'alternative_routes': processed_routes[1:] if len(processed_routes) > 1 else [],
            'total_routes': len(processed_routes)
        })
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


def _is_near_path(lat, lng, path_coords, max_km=10):
    """Check if point is near path"""
    for coord in path_coords:
        if haversine_distance(lat, lng, coord[1], coord[0]) <= max_km:
            return True
    return False


def get_all_locations(request):
    """Get all locations"""
    return JsonResponse({
        'tourist_attractions': list(TouristAttraction.objects.filter(is_active=True).values(
            'id', 'name', 'latitude', 'longitude', 'category', 'rating', 'address'
        )),
        'ev_stations': list(EVChargingStation.objects.filter(is_active=True).values(
            'id', 'name', 'latitude', 'longitude', 'charger_type', 'power_level', 'address'
        ))
    })