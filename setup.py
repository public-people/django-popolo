import os

from setuptools import find_packages, setup


def read_file(filename):
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        with open(filepath, encoding='utf-8') as f:
            return f.read()
    except OSError:
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
    url='https://github.com/public-people/django-popolo',
    license='AGPL-3.0-or-later',
    description=' '.join(__import__('popolo').__doc__.splitlines()).strip(),
    long_description=read_file('README.rst'),
    long_description_content_type='text/x-rst',
    python_requires='>=3.12',
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Framework :: Django',
        'Framework :: Django :: 6.0',
        'Framework :: Django :: 6.1',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
    ],
    zip_safe=False,
    install_requires=[
        'Django>=6.1',
        'django-model-utils>=5.0.0',
        'django-simple-history>=3.13.0',
        'django-ajax-selects>=3.0.3',
    ],
    extras_require={
        'test': [
            'coverage>=7.17.0',
            'Faker>=40.44.0',
        ],
    },
)
