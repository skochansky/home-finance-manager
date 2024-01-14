from django.core.management.utils import get_random_secret_key

from .settings import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
    }
}


SECRET_KEY = get_random_secret_key()

DEBUG = False
