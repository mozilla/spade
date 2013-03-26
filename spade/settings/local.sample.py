"""
Settings overrides for a particular deployment of this app. The defaults should
be suitable for local development; other settings below are likely to need
adjustment for a staging or production deployment.

Copy local.sample.py to local.py and modify as needed.
"""
# Local settings (overrides)
import os

DATABASES = {
    "default": {
        "ENGINE"   : "django.db.backends.mysql",
        "NAME"     : os.environ.get("SPADE_DATABASE_NAME", ""),
        "USER"     : os.environ.get("SPADE_DATABASE_USER", ""),
        "PASSWORD" : os.environ.get("SPADE_DATABASE_PASSWORD", ""),
        "HOST"     : os.environ.get("SPADE_DATABASE_HOST", "localhost"),
        "PORT"     : os.environ.get("SPADE_DATABASE_PORT", ""),
        'OPTIONS': {
            "init_command": "SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED; SET storage_engine=InnoDB;"
        },
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'CHANGETHISFJKDFJDKFJDK#%^&JDKJDKFDK@K$%^KJ#K%J^K^JK@CHANGETHIS'

# Settings below here don't need to be changed if the defaults suffice

# Change this to store scraped files somewhere other than the local filesystem
# (e.g. the S3 backend in the django-storages project). The MEDIA_* settings
# below are only relevant if FileSystemStorage (the default) is used.
#DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = join(BASE_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
#MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
#STATIC_ROOT = join(BASE_PATH, 'assets')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
#STATIC_URL = '/static/'
