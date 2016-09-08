import json

from mock import Mock, call

from django.test import TestCase

from popolo.importers.popit import PopItImporter
from popolo import models

# There are some very basic tests here.  For when there is time, the
# following things could be added or improved:
#
#  * Test creation of areas
#  * Test creation of posts
#  * Test creation of contact details
#  * Test creation of links
#  * Test creation of sources
#  * Test creation of other names
#  * Test creation of generic identifiers
#  * Test updates rather than creation of the above
#  * Tests for the legislative_period_id in memberships special case
#  * Test setting of a parent area
#  * Test setting of a parent organisation
#  * Test handling of areas on posts
#  * Test the show_data_on_error context manager
#  * Test that objects that have disappeared are removed (not yet implemented)

class BasicImporterTests(TestCase):

    def test_all_top_level_optional(self):
        # This just check that you don't get an exception when
        # importing empty Popolo JSON.
        input_json = '{}'
        data = json.loads(input_json)
        importer = PopItImporter()
        importer.import_from_export_json_data(data)

    def test_simplest_person(self):
        input_json = '''
{
    "persons": [
        {
            "id": "a1b2",
            "name": "Alice"
        }

    ],
    "organizations": [],
    "memberships": []
}
'''
        data = json.loads(input_json)
        importer = PopItImporter()
        importer.import_from_export_json_data(data)
        self.assertEqual(models.Person.objects.count(), 1)
        person = models.Person.objects.get()
        self.assertEqual(person.name, "Alice")
        self.assertEqual(
            person.identifiers.get(scheme='popit-person').identifier,
            "a1b2")

    def test_person_with_membership(self):
        input_json = '''
{
    "persons": [
        {
            "id": "a1b2",
            "name": "Alice"
        }

    ],
    "organizations": [
        {
            "id": "commons",
            "name": "House of Commons"
        }
    ],
    "memberships": [
        {
            "person_id": "a1b2",
            "organization_id": "commons"
        }
    ]
}
'''
        data = json.loads(input_json)
        importer = PopItImporter()
        importer.import_from_export_json_data(data)
        self.assertEqual(models.Membership.objects.count(), 1)
        self.assertEqual(models.Person.objects.count(), 1)
        self.assertEqual(models.Organization.objects.count(), 1)
        person = models.Person.objects.get()
        self.assertEqual(person.name, "Alice")
        organization = models.Organization.objects.get()
        self.assertEqual(organization.name, "House of Commons")
        self.assertEqual(
            organization.identifiers.get(scheme='popit-organization').identifier,
            "commons"
        )
        membership = models.Membership.objects.get()
        self.assertEqual(membership.person, person)
        self.assertEqual(membership.organization, organization)

    def test_person_with_inline_membership(self):
        input_json = '''
{
    "persons": [
        {
            "id": "a1b2",
            "name": "Alice",
            "memberships": [
                {
                    "person_id": "a1b2",
                    "organization_id": "commons"
                }
            ]
        }

    ],
    "organizations": [
        {
            "id": "commons",
            "name": "House of Commons"
        }
    ]
}
'''
        data = json.loads(input_json)
        importer = PopItImporter()
        importer.import_from_export_json_data(data)
        self.assertEqual(models.Membership.objects.count(), 1)
        self.assertEqual(models.Person.objects.count(), 1)
        self.assertEqual(models.Organization.objects.count(), 1)
        person = models.Person.objects.get()
        self.assertEqual(person.name, "Alice")
        organization = models.Organization.objects.get()
        self.assertEqual(organization.name, "House of Commons")
        self.assertEqual(
            organization.identifiers.get(scheme='popit-organization').identifier,
            "commons"
        )
        membership = models.Membership.objects.get()
        self.assertEqual(membership.person, person)
        self.assertEqual(membership.organization, organization)


    def test_custom_identifier_prefix(self):
        input_json = '''
{
    "persons": [
        {
            "id": "a1b2",
            "name": "Alice"
        }

    ],
    "organizations": [
        {
            "id": "commons",
            "name": "House of Commons"
        }
    ]
}
'''
        data = json.loads(input_json)
        importer = PopItImporter(id_prefix='popolo:')
        importer.import_from_export_json_data(data)
        self.assertEqual(models.Person.objects.count(), 1)
        self.assertEqual(models.Organization.objects.count(), 1)
        person = models.Person.objects.get()
        organization = models.Organization.objects.get()
        person_identifier = person.identifiers.get()
        organization_identifier = organization.identifiers.get()
        self.assertEqual(person_identifier.scheme, 'popolo:person')
        self.assertEqual(person_identifier.identifier, 'a1b2')
        self.assertEqual(organization_identifier.scheme, 'popolo:organization')
        self.assertEqual(organization_identifier.identifier, 'commons')

    def test_creates_new_person_if_not_found(self):
        existing_person = models.Person.objects.create(name='Algernon')
        input_json = '''
{
    "persons": [
        {
            "id": "a1b2",
            "name": "Alice"
        }
    ]
}
'''
        data = json.loads(input_json)
        importer = PopItImporter()
        importer.import_from_export_json_data(data)
        self.assertEqual(models.Person.objects.count(), 2)
        new_person = models.Person.objects.exclude(pk=existing_person.id).get()
        new_person_identifier = new_person.identifiers.get()
        self.assertEqual(new_person_identifier.scheme, 'popit-person')
        self.assertEqual(new_person_identifier.identifier, 'a1b2')

    def test_updates_person_if_found(self):
        existing_person = models.Person.objects.create(name='Algernon')
        existing_person.identifiers.create(
            scheme='popolo:person',
            identifier="a1b2"
        )
        input_json = '''
{
    "persons": [
        {
            "id": "a1b2",
            "name": "Alice"
        }
    ]
}
'''
        data = json.loads(input_json)
        importer = PopItImporter(id_prefix='popolo:')
        mock_observer = Mock()
        importer.add_observer(mock_observer)
        importer.import_from_export_json_data(data)
        self.assertEqual(models.Person.objects.count(), 1)
        # Reget the person from the database:
        person = models.Person.objects.get(pk=existing_person.id)
        self.assertEqual(person.name, 'Alice')
        # Check that the observer was called with created=False:
        self.assertEqual(mock_observer.notify.call_count, 1)
        self.assertEqual(
            mock_observer.notify.call_args,
            call(
                'person',
                existing_person,
                False,
                {
                    "id": "a1b2",
                    "name": "Alice"
                }
            )
        )

    def test_observer_called(self):
        input_json = '''
{
    "persons": [
        {
            "id": "a1b2",
            "name": "Alice"
        }
    ],
    "organizations": [
        {
            "id": "commons",
            "name": "House of Commons"
        }
    ],
    "memberships": [
        {
            "person_id": "a1b2",
            "organization_id": "commons",
            "post_id": "65808"
        }
    ],
    "areas": [
        {
            "id": 100,
            "name": "Dulwich and West Norwood",
            "identifier": "gss:E14000673"
        }
    ],
    "posts": [
        {
            "id": "65808",
            "url": "https://candidates.democracyclub.org.uk/api/v0.9/posts/65808/",
            "label": "Member of Parliament for Dulwich and West Norwood",
            "role": "Member of Parliament",
            "organization_id": "commons",
            "group": "England",
            "area_id": 100
        }
    ]
}
'''
        data = json.loads(input_json)
        importer = PopItImporter()
        mock_observer = Mock()
        importer.add_observer(mock_observer)
        importer.import_from_export_json_data(data)
        # Just as a double-check, make sure that one of each of these
        # objects has been created:
        self.assertEqual(models.Person.objects.count(), 1)
        self.assertEqual(models.Organization.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 1)
        self.assertEqual(models.Area.objects.count(), 1)
        self.assertEqual(models.Post.objects.count(), 1)
        # Now check that the observer has been called for each one.
        self.assertEqual(mock_observer.notify.call_count, 5)
        # And check that the payload for each call is correct:
        self.assertEqual(
            mock_observer.notify.call_args_list,
            [
                call(
                   'area',
                    models.Area.objects.get(),
                    True,
                    {
                        "id": 100,
                        "name": "Dulwich and West Norwood",
                        "identifier": "gss:E14000673"
                    },
                ),
                call(
                    'organization',
                    models.Organization.objects.get(),
                    True,
                    {
                        "id": "commons",
                        "name": "House of Commons"
                    },
                ),
                call(
                    'post',
                    models.Post.objects.get(),
                    True,
                    {
                        "id": "65808",
                        "url": "https://candidates.democracyclub.org.uk/api/v0.9/posts/65808/",
                        "label": "Member of Parliament for Dulwich and West Norwood",
                        "role": "Member of Parliament",
                        "organization_id": "commons",
                        "group": "England",
                        "area_id": 100
                    },
                ),
                call(
                    'person',
                    models.Person.objects.get(),
                    True,
                    {
                        'id': 'a1b2',
                        'name': 'Alice'
                    }
                ),
                call(
                    'membership',
                    models.Membership.objects.get(),
                    True,
                    {
                        'person_id': 'a1b2',
                        'organization_id': 'commons',
                        'id': 'missing_commons_missing_missing_missing_a1b2',
                        'post_id': '65808'
                    }
                )
            ]
        )
