Installation
============

1. Install MySQL.

2. Install the dependencies in ``requirements/compiled.txt`` either via
   system-level package manager, or with ``pip install -r
   requirements/compiled.txt`` (preferably into a `virtualenv`_ in the latter
   case).

3. If you will need to run the tests or work on Spade development, install the
   development-only dependencies into your virtualenv with ``pip install -r
   requirements/dev.txt``.

3. Copy ``spade/settings/local.sample.py`` to ``spade/settings/local.py`` and
   modify the settings as appropriate for your installation.

4. Run ``./manage.py syncdb`` to create the database tables.

.. _virtualenv: http://www.virtualenv.org
