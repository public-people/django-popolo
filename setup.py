import os
from setuptools import setup, find_packages


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


setup(
    name='mysociety-django-popolo',
    version=__import__('popolo').__version__,
    author='Guglielmo Celata',
    author_email='guglielmo@openpolis.it',
    maintainer='Matthew Somerville',
    maintainer_email='matthew@mysociety.org',
    packages=find_packages(),
    include_package_data=True,
    url='http://github.com/mysociety/django-popolo',
    license='Affero',
    description=u' '.join(__import__('popolo').__doc__.splitlines()).strip(),
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
    ],
    long_description=read_file('README.rst'),
    test_suite="runtests.runtests",
    zip_safe=False,
    tests_require=['fake-factory'],
    install_requires=[
        "django-model-utils",
        "django-simple-history==2.0",
        "django-ajax-selects==1.7.1",
    ],
)
