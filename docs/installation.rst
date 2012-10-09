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

Vagrant Setup
-------------

1. Run ``vagrant up`` in a terminal. This will create a new VM that will have
   Spade running on it. It will run the necessary `Puppet`_ scripts

2. add ``127.0.0.1  dev.spade.org`` to /etc/hosts

3. Navigate to http://dev.spade.org:8000 in your browser

.. _virtualenv: http://www.virtualenv.org
.. _Puppet: http://puppetlabs.com/
