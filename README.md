# alx-backend-caching_property_listings

A Django project that powers a simple **Property Listings** API with **PostgreSQL** and **Redis** via Docker.  
Responses are cached at two layers:

- **View cache**: `/properties/` endpoint cached for **15 minutes**
- **Low-level cache**: the queryset backing the list cached for **1 hour**
- **Signals**: automatic cache invalidation on create/update/delete
- **Metrics**: `/properties/cache-metrics/` to inspect Redis hit/miss ratio

---

## Stack

- **Django 5**
- **PostgreSQL** (Docker)
- **Redis** (Docker) + `django-redis`

---

## Quickstart

### 1. Clone & install

```bash
git clone https://github.com/mpyatt/alx-backend-caching_property_listings.git
cd alx-backend-caching_property_listings
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
````

### 2. Bring up Postgres & Redis

```bash
docker compose up -d
# postgres -> 127.0.0.1:5432
# redis    -> 127.0.0.1:6379
```

### 3. Configure env (optional)

Create `.env` (or export env vars in your shell):

```bash
# .env (example)
DJANGO_SECRET_KEY=dev-secret-key
DEBUG=1
ALLOWED_HOSTS=127.0.0.1,localhost

POSTGRES_DB=property_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=127.0.0.1   # use "postgres" if Django runs in Docker
POSTGRES_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/1  # use redis://redis:6379/1 if Django runs in Docker
```

### 4. Migrate & run

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Open: [http://127.0.0.1:8000/properties/](http://127.0.0.1:8000/properties/)

---

## API

### `GET /properties/`

Returns all properties as JSON.

```bash
curl http://127.0.0.1:8000/properties/
```

Example response:

```json
{
  "properties": [
    {
      "id": 1,
      "title": "Two-bedroom Apartment",
      "description": "Top floor, sea view",
      "price": "1200.00",
      "location": "Accra",
      "created_at": "2025-08-31T18:45:12.345678Z"
    }
  ]
}
```

### `GET /properties/cache-metrics/`

Returns Redis keyspace hits/misses and hit ratio (never cached).

```bash
curl http://127.0.0.1:8000/properties/cache-metrics/
```

Example response:

```json
{
  "metrics": {
    "keyspace_hits": 10,
    "keyspace_misses": 3,
    "total_requests": 13,
    "hit_ratio": 0.7692307692307693
  }
}
```

---

## Seeding Data

Creates realistic sample data.

```bash
python manage.py seed_properties --count 25
# or reset and seed:
python manage.py seed_properties --flush --count 40
```

> After seeding, the list caches are invalidated automatically by signals; the command also clears `"all_properties"` explicitly.

---

## Caching Design

- **Per-view cache**: `@cache_page(60 * 15)` on `property_list` (15 minutes)
- **Low-level cache**: `properties/utils.py:get_all_properties()` caches the data list in Redis for 1 hour (`cache.set('all_properties', ..., 3600)`)
- **Signals**: `post_save` & `post_delete` on `Property` call `cache.delete('all_properties')` to invalidate

You can also inspect cache performance:

```python
from properties.utils import get_redis_cache_metrics
print(get_redis_cache_metrics())
# {'keyspace_hits': 10, 'keyspace_misses': 3, 'total_requests': 13, 'hit_ratio': 0.769...}
```

---

## Project Structure (key files)

```sh
alx-backend-caching_property_listings/
├── docker-compose.yaml
├── requirements.txt
├── manage.py
├── alx_backend_caching_property_listings/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── properties/
    ├── apps.py
    ├── __init__.py
    ├── management/
    │   └── commands/
    │       └── seed_properties.py
    ├── models.py
    ├── signals.py
    ├── utils.py
    ├── views.py
    └── urls.py
```

---

## Troubleshooting

- **`psycopg2.OperationalError: could not connect to server`**
  Ensure Postgres is up: `docker compose ps` and that `POSTGRES_HOST/PORT` match how you’re running Django (host vs Docker network).

- **`redis.exceptions.ConnectionError`**
  Ensure Redis is up and `REDIS_URL` points to `127.0.0.1:6379` (host) or `redis:6379` (Docker network).

- **Cache not invalidating**
  Check that `properties.apps.PropertiesConfig` is in `INSTALLED_APPS` and that `apps.py#ready()` imports `signals`.
