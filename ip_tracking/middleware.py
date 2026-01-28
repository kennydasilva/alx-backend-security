from .models import RequestLog, BlockedIP
from django.http import HttpResponseForbidden
from django.core.cache import cache
import ipinfo

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response=get_response
    
    def __call__(self, request):
        ip_address= self.get_client_ip(request)


        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Access denied: your IP is blocked.")

        geo_data=self.get_geolocation(ip_address)

        RequestLog.objects.create(
            ip_address=ip_address,
            path=request.path,
            country=geo_data.get("country"),
            city=geo_data.get("city")
        )

        response= self.get_response(request)
        
    

    def get_client_ip(self, request):
        x_forwarded_for=request.META.get('HTTP_X-FORWARDEDED_FOR')

        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        
        return request.META.get('REMOTE_ADDR')
    
    def get_geolocation(self, ip_address):
        cache_key=f"geo_{ip_address}"
        cached= cache.get(cache_key)

        if cached:
            return cached
        
        try:
            details=self.ipinfo_handler.getDetails(ip_address)
            geo_data={
                "country":details.country,
                "city":details.city,
            }
        except Exception:
            geo_data={"country": None, "city": None}
        

        cache.set(cache_key, geo_data)
        return geo_data
        