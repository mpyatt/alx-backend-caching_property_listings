from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from .utils import get_all_properties


@cache_page(60 * 15)  # 15 minutes
def property_list(request):
    """
    Returns JSON list of properties. Response is cached for 15 minutes,
    and the underlying list is also cached at the data level for 1 hour.
    """
    rows = get_all_properties()

    # Ensure JSON-safe values (Decimal & datetime)
    data = []
    for r in rows:
        data.append({
            "id": r["id"],
            "title": r["title"],
            "description": r["description"],
            "price": str(r["price"]),
            "location": r["location"],
            "created_at": r["created_at"].isoformat() if hasattr(r["created_at"], "isoformat") else r["created_at"],
        })

    return JsonResponse({"properties": data})
