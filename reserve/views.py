# Create your views here.
import os
from dotenv import load_dotenv
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import dotenv
from .forms import CustomerRegistrationForm
from .models import UserProfile

load_dotenv()
GOOGLE_API_KEY = os.getenv('AIzaSyBJod7t2x-K64ayGTIICQDR9R7dCm1ydnI')  # ✅ safe way to load API key from .env file


def index(request):
    return render(request, 'index.html')
def base(request):
    return render(request, 'base.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def register(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            # user.username = form.cleaned_data['email']  # Use email as username
            user.set_password(form.cleaned_data['password1'])
            user.save()

            # ✅ Get the role the user selected from the form
            role = form.cleaned_data['role']
            UserProfile.objects.create(user=user, role=role)

            login(request, user)

            # ✅ Redirect based on role
            if role == 'hotel_owner':
                return redirect('dashboard')
            else:
                return redirect('index')
        else:
            messages.error(request, "Please fix the errors below.")

    else:
        form = CustomerRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

# @csrf_exempt
# def hotelsAPI(request):
#     if request.method == "POST":
#         # Handle POST request to create a new hotel
#         url = f"enter the url of the api here"
#         response = requests.post(url, data=request.POST)
#         if response.status_code == 200:
#             raw_data = response.json()
#             # Process raw_data as needed and create Hotel objects
#             results=raw_data.get()#('results')  # Adjust this based on the actual structure of the API response   )
#             for result in results:
#                 data=json.dumps(result)
#                 # Create all the needed fiels from the data and save to database
#                 #Example:
#                 #name=result.get('name')
#                 # location =result.get('location') and so on for others
#                 #if it contains sub-fields like firstname & lastname
#                 #hotel=name_of_the_model_in_which_you_want_to_store.objects.create(
#                 # name=name.get(firstname) + " " + name.get(lastname),
#                 # other_field=result.get('other_field'),
#                 # if it doesn't contain sub-fields like firstname & lastname
#                 # location=location
                 
#                 #)
                
#                 #destination=result.get('destination')
                

                
    
#     elif request.method == "GET":
#         # Handle GET request to list hotels
#         pass
#     return render(request, 'hotels_api.html') 
# api key for testing purposes only, please replace it with your own key


#          AIzaSyBJod7t2x-K64ayGTIICQDR9R7dCm1ydnI

           
############################################################################
# The following code is for testing purposes only, it is not used in the project
############################################################################        
import requests
from django.shortcuts import render
from django.contrib import messages
from .models import Hotel

GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"  # ✅ paste your key here

def get_photo_url(photo_reference):
    # ✅ This builds the image URL from the photo reference Google returns
    if photo_reference:
        return (
            f"https://maps.googleapis.com/maps/api/place/photo"
            f"?maxwidth=800"
            f"&photoreference={photo_reference}"
            f"&key={GOOGLE_API_KEY}"
        )
    return None  # return None if no photo available


def hotelsAPI(request):
    if request.method == "POST":
        city = request.POST.get('city', 'London')

        try:
            # ─── Step 1: Get coordinates of the city ───────────────────
            geocode_url = (
                f"https://maps.googleapis.com/maps/api/geocode/json"
                f"?address={city}&key={GOOGLE_API_KEY}"
            )
            geo_response = requests.get(geocode_url).json()

            if not geo_response['results']:
                messages.error(request, f"City '{city}' not found.")
                return render(request, 'hotels_api.html', {'hotels': Hotel.objects.all()})

            location = geo_response['results'][0]['geometry']['location']
            lat, lng = location['lat'], location['lng']

            # ─── Step 2: Search for hotels near the city ───────────────
            places_url = (
                f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                f"?location={lat},{lng}"
                f"&radius=5000"
                f"&type=lodging"
                f"&key={GOOGLE_API_KEY}"
            )
            places_response = requests.get(places_url).json()
            results = places_response.get('results', [])

            if not results:
                messages.warning(request, f"No hotels found in {city}.")

            for result in results:
                # ─── Step 3: Extract photo reference ───────────────────
                photos         = result.get('photos', [])
                photo_ref      = photos[0].get('photo_reference') if photos else None
                image_url      = get_photo_url(photo_ref)  # ✅ build the image URL

                name           = result.get('name', 'Unknown Hotel')
                address        = result.get('vicinity', 'N/A')
                rating         = result.get('rating', None)
                hotel_lat      = result['geometry']['location']['lat']
                hotel_lng      = result['geometry']['location']['lng']

                # ─── Step 4: Save to database ──────────────────────────
                Hotel.objects.get_or_create(
                    name=name,
                    defaults={
                        'location' : city,
                        'address'  : address,
                        'lat'      : hotel_lat,
                        'lng'      : hotel_lng,
                        'image_url': image_url,  # ✅ save image URL
                    }
                )

            messages.success(request, f"Hotels in {city} loaded successfully!")

        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")

    hotels = Hotel.objects.all()
    return render(request, 'hotels_api.html', {'hotels': hotels})


############################################################################ 
""" this is to secure the API key
bash 
pip install python-dotenv
```

Create a `.env` file in your project root:
```
GOOGLE_API_KEY=your_actual_key_here

views.py
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')  # ✅ safe
"""
##########################################################################


