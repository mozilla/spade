Installation
============

1. Install MySQL.

2. Install the dependencies in ``requirements/compiled.txt`` either via
   system-level package manager, or with ``pip install -r
   requirements/compiled.txt``.

3. Copy ``spade/settings/local.sample.py`` to ``spade/settings/local.py`` and
   modify the settings as appropriate for your installation.

4. Run ``./manage.py syncdb`` to create the database tables.

