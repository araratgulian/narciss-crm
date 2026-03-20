import django
from django.conf import settings

# Ensure Django settings are configured for pytest
if not settings.configured:
    settings.configure()
    django.setup()
