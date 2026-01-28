from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

@require_POST
@ratelimit(key='ip', rate='5/m', block=True)
def login_view(request):
    """ Login endpoint (rate limited).
    Anonymous users:5 requests/min
    Authenticated users: 10 requests/min"""

    if request.user.is_authenticated:
        return authenticate_login(request)
    
    return JsonResponse({"message": "Login attempt processed"})


@ratelimit(key='ip', rate='10/m', block=True)
def authenticated_login(request):
    return JsonResponse({"message": "Authenticated user login attempt"})