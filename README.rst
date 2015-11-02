popolo
========================


.. image:: https://travis-ci.org/mysociety/django-popolo.svg?branch=master
  :target: https://travis-ci.org/mysociety/django-popolo

.. image:: https://coveralls.io/repos/mysociety/django-popolo/badge.svg?branch=master&service=github
  :target: https://coveralls.io/github/mysociety/django-popolo?branch=master


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

Running the Tests
------------------------------------

Set up the tests with:

    pip install -r tests_requirements.txt
    python setup.py install

You can run the tests with::

    python setup.py test

or::

    python runtests.py
