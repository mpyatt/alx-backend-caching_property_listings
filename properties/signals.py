from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Property

ALL_PROPERTIES_KEY = "all_properties"


@receiver(post_save, sender=Property)
def invalidate_on_save(sender, instance, **kwargs):
    cache.delete(ALL_PROPERTIES_KEY)


@receiver(post_delete, sender=Property)
def invalidate_on_delete(sender, instance, **kwargs):
    cache.delete(ALL_PROPERTIES_KEY)
