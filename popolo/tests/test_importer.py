import json

from django.test import TestCase

from popolo.importers.popit import PopItImporter
from popolo.models import Membership, Organization, Person

class BasicImporterTests(TestCase):

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
        self.assertEqual(Person.objects.count(), 1)
        person = Person.objects.get()
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
        self.assertEqual(Membership.objects.count(), 1)
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(Organization.objects.count(), 1)
        person = Person.objects.get()
        self.assertEqual(person.name, "Alice")
        organization = Organization.objects.get()
        self.assertEqual(organization.name, "House of Commons")
        self.assertEqual(
            organization.identifiers.get(scheme='popit-organization').identifier,
            "commons"
        )
        membership = Membership.objects.get()
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
        self.assertEqual(Membership.objects.count(), 1)
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(Organization.objects.count(), 1)
        person = Person.objects.get()
        self.assertEqual(person.name, "Alice")
        organization = Organization.objects.get()
        self.assertEqual(organization.name, "House of Commons")
        self.assertEqual(
            organization.identifiers.get(scheme='popit-organization').identifier,
            "commons"
        )
        membership = Membership.objects.get()
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
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(Organization.objects.count(), 1)
        person = Person.objects.get()
        organization = Organization.objects.get()
        person_identifier = person.identifiers.get()
        organization_identifier = organization.identifiers.get()
        self.assertEqual(person_identifier.scheme, 'popolo:person')
        self.assertEqual(person_identifier.identifier, 'a1b2')
        self.assertEqual(organization_identifier.scheme, 'popolo:organization')
        self.assertEqual(organization_identifier.identifier, 'commons')
