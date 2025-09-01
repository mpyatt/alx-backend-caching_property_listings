from django.urls import path
from properties.views import property_list, cache_metrics

urlpatterns = [
    path("", property_list, name="property-list"),
    path("cache-metrics/", cache_metrics, name="cache-metrics"),
]
