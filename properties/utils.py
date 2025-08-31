import logging
from django.core.cache import cache
from django_redis import get_redis_connection
from .models import Property

logger = logging.getLogger(__name__)

CACHE_KEY_ALL_PROPERTIES = "all_properties"


def get_all_properties():
    """
    Returns a serialized list of properties from Redis if available,
    otherwise queries the DB, caches for 1 hour, and returns the list.
    """
    data = cache.get(CACHE_KEY_ALL_PROPERTIES)
    if data is None:
        qs = Property.objects.all().values(
            "id", "title", "description", "price", "location", "created_at"
        )
        data = list(qs)
        cache.set(CACHE_KEY_ALL_PROPERTIES, data, timeout=3600)  # 1 hour
    return data


def get_redis_cache_metrics():
    """
    Fetch Redis INFO and compute hit ratio.
    Ensures the literal check for: 'if total_requests > 0 else 0'
    """
    try:
        conn = get_redis_connection("default")
        info = conn.info()
        hits = int(info.get("keyspace_hits", 0))
        misses = int(info.get("keyspace_misses", 0))
        total_requests = hits + misses
        hit_ratio = (hits / total_requests) if total_requests > 0 else 0

        metrics = {
            "keyspace_hits": hits,
            "keyspace_misses": misses,
            "total_requests": total_requests,
            "hit_ratio": hit_ratio,
        }
        logger.info("Redis cache metrics: %s", metrics)
        return metrics
    except Exception as e:
        logger.error("Failed to fetch Redis cache metrics: %s", e)
        return {"error": str(e)}
