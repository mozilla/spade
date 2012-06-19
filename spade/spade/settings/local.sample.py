"""
Settings overrides for a particular deployment of this app. The defaults should
be suitable for local development; other settings below are likely to need
adjustment for a staging or production deployment.

Copy local.sample.py to local.py and modify as needed.
"""

# Local settings (overrides)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'myuser_spade',               # Or path to database file if using sqlite3.
        'USER': 'myuser',                     # Not used with sqlite3.
        'PASSWORD': 'mypass',                 # Not used with sqlite3.
        'HOST': '',                           # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                           # Set to empty string for default. Not used with sqlite3.
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'CHANGETHISFJKDFJDKFJDK#%^&JDKJDKFDK@K$%^KJ#K%J^K^JK@CHANGETHIS'

