##################
Django-Phabricator
##################

Module for importing and working with `Phabricator <http://phabricator.org/>`_ data.  Currently focuses on reporting on "diffs".

============
Installation
============

Install with ``pip``::

   pip install git+https://github.com/TidalLabs/django-phabricator.git#egg=django-phabricator

[PyPi package TBA]

Add ``dj_phab`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        # ...
        'dj_phab',
    )

If you intend to import data, create a ``.arcrc`` file in your home directory.  If you have `Arcanist <https://secure.phabricator.com/book/phabricator/article/arcanist/>`_ installed, this can be done with::

   arc install-certificate <URI of Phabricator instance>

==============
Importing Data
==============

Django-phabricator can import or update data from your Phabricator instance::

   python manage.py import_from_phabricator

Depending on the quantity of data you have, initial import may take a long time.  Subsequent imports should run more quickly.  Setting up a cron job to keep data up to date is recommended if your Phabricator instance is in active use.

========================
Using Built-In Reporting
========================

Django-phabricator provides a few reports by default [currently only statistics about code reviews].  You can make these reports available on your site either by hooking up the built-in views (documentation coming soon) to a custom URLconf, or by including the django-phabricator default urlconf in your site's primary URLconf:

.. code-block:: python

    urlpatterns = patterns(
        ...
        url(r'^phabricator-stats/', include('dj_phab.urls')),
    )

============
Requirements
============

Django-phabricator has been tested with Python 2.7 and Django 1.7.  It relies on `django-model-utils <https://django-model-utils.readthedocs.org/en/latest/>`_ and `python-phabricator <https://github.com/disqus/python-phabricator>`_.