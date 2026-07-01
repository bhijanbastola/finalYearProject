# maps/decorators.py
# Custom decorator to restrict views to "hotel_owner" role only
# Matches your UserProfile model (user.profile.role)

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def owner_required(view_func):
    """
    Decorator that ensures the logged-in user has a UserProfile
    with role='hotel_owner' before allowing access to add/edit
    location forms.

    Superusers are always allowed through, even if they have no
    UserProfile (e.g. created via `createsuperuser`).

    Usage:
        @owner_required
        def add_attraction(request):
            ...
    """
    @wraps(view_func)
    @login_required(login_url='login')  # change 'login' if your login url name differs
    def wrapper(request, *args, **kwargs):
        
        # Superusers always pass through — no role check needed
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Get the user's profile safely (in case it doesn't exist for some reason)
        profile = getattr(request.user, 'profile', None)
        user_role = profile.role if profile else None
        
        if user_role != 'hotel_owner':
            messages.error(
                request, 
                "You don't have permission to add locations. Only hotel owners can do this."
            )
            return redirect('maps:map_view')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
