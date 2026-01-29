from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, SuspiciousIP
from django.db import models


@shared_task
def detect_suspicious_ips():
    """ 
    Detect IPs with abnormal beaviour:
    - More than 100 requests per hour
    - Acess to sensitive paths
    """

    one_hour_ago=timezone.now() - timedelta(hours=1)

    logs_last_hour=(
        RequestLog.objects
        .filter(timestamp_gte=one_hour_ago)
        .values('ip_address')
        .annotate(request_count=models.Count('id'))
        .filter(request_count_gt=100)
    )


    for entry in logs_last_hour:
        SuspiciousIP.objects.get_or_create(
            ip_address=entry['ip_address'],
            reason="Exceeeded 100 requests per hour"
        )


    sensitive_paths=['/admin', '/login']

    suspicius_logs=RequestLog.objects.filter(
        path_in=sensitive_paths,
        timestamp_gte=one_hour_ago
    )


    for log in suspicius_logs:
        SuspiciousIP.objects.get_or_create(
            ip_address=log.ip_address,
            reason=f"accessed sensitive path: {log.path}"
        )