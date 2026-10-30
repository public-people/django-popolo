popolo
========================


.. image:: https://github.com/public-people/django-popolo/actions/workflows/tests.yml/badge.svg
  :target: https://github.com/public-people/django-popolo/actions/workflows/tests.yml


Welcome to the documentation for django-popolo!


This fork of django-popolo is the same as the `upstream code
<https://github.com/openpolis/django-popolo>`_ except that the models use
integer IDs rather than slugs, and the models have no slug field. This is to
enable projects using this package to pick their own (perhaps different) slug
behaviour.


**django-popolo** is a django-based implementation of the
`Popolo's open government data specifications <http://popoloproject.com/>`_.

It is developed as a django application to be deployed directly within django projects.

It will allow web developers using it to manage and store data according to Popolo's specifications.

The standard sql-oriented django ORM will be used.

Project is under way and any help is welcome.


Installation
------------

To install ``django-popolo`` as a third party app within a Django project, you
need to add it to the Django project's requirements.txt. You can do this from
GitHub in the usual way, or using the ``mysociety-django-popolo`` package on
PyPI.

You also need to add ``popolo``, ``ajax_select`` and ``simple_history`` to your
Django ``INSTALLED_APPS``.

This fork requires Python 3.12+ and Django 6.1+.


Running the Tests
------------------------------------

Set up the tests with:

.. code:: bash

    python -m pip install -e ".[test]"

You can run the tests with:

.. code:: bash

    python runtests.py

The test suite also runs automatically in GitHub Actions.
