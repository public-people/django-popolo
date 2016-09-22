# -*- coding: utf-8 -*-

from contextlib import contextmanager
import json
import sys

from mock import Mock, call
from django.utils import six

from django.core.exceptions import ValidationError
from django.test import TestCase

from popolo.importers.popit import PopItImporter
from popolo import models

# There are some very basic tests here.  For when there is time, the
# following things could be added or improved:
#
#  * Test creation of sources
#  * Test creation of other names
#  * Test updates as well as creation of all objects
#  * Tests for the legislative_period_id in memberships special case
#  * Test setting of a parent area
#  * Test setting of a parent organisation
#  * Test handling of areas on posts
#  * Test the show_data_on_error context manager
#  * Test that objects that have disappeared are removed (not yet implemented)


@contextmanager
def capture_output():
    # Suggested here: http://stackoverflow.com/a/17981937/223092
    new_out, new_err = six.StringIO(), six.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield new_out, new_err
    finally:
        sys.stdout, sys.stderr = old_out, old_err


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

    def test_related_objects_for_person(self):
        input_json = '''
{
    "persons": [
        {
            "id": "a1b2",
            "name": "Alice",
            "identifiers": [
                {
                    "identifier": "123456789",
                    "scheme": "yournextmp-candidate"
                }
            ],
            "contact_details": [
                {
                    "contact_type": "twitter",
                    "label": "",
                    "note": "",
                    "value": "sometwitterusernameorother"
                }

            ],
            "links": [
                {
                    "note": "homepage",
                    "url": "http://example.com/alice"
                }
            ]
        }
    ]
}
'''
        data = json.loads(input_json)
        importer = PopItImporter()
        importer.import_from_export_json_data(data)
        self.assertEqual(models.Person.objects.count(), 1)
        person = models.Person.objects.get()
        self.assertEqual(person.name, "Alice")
        self.assertEqual(person.identifiers.count(), 2)
        self.assertEqual(
            person.identifiers.get(scheme='popit-person').identifier,
            "a1b2")
        self.assertEqual(
            person.identifiers.get(scheme='yournextmp-candidate').identifier,
            "123456789")
        self.assertEqual(person.contact_details.count(), 1)
        contact_detail = person.contact_details.get()
        self.assertEqual(contact_detail.contact_type, 'twitter')
        self.assertEqual(contact_detail.value, 'sometwitterusernameorother')
        self.assertEqual(person.links.count(), 1)
        link = person.links.get()
        self.assertEqual(link.note, 'homepage')
        self.assertEqual(link.url, 'http://example.com/alice')

    def test_truncation_unknown_option(self):
        with self.assertRaises(ValueError):
            PopItImporter(truncate='dunno')

    def test_truncation_none(self):
        long_name = ('Albert ' * 100).strip()
        input_json = '''
{{
    "persons": [
        {{
            "id": "a1b2",
            "name": "{0}"
        }}
    ]
}}
'''.format(long_name)
        data = json.loads(input_json)
        # With truncate='yes', there should be no exception:
        importer = PopItImporter(truncate='yes')
        importer.import_from_export_json_data(data)
        person = models.Person.objects.get()
        max_length = person._meta.get_field('name').max_length
        truncated_name = long_name[:max_length]
        self.assertEqual(person.name, truncated_name)

    def test_truncation_exception(self):
        long_name = ('Albert ' * 100).strip()
        input_json = '''
{{
    "persons": [
        {{
            "id": "a1b2",
            "name": "{0}"
        }}
    ]
}}
'''.format(long_name)
        data = json.loads(input_json)
        # With the default, truncate='exception', there should be an
        # exception raised:
        importer = PopItImporter()
        with self.assertRaisesRegexp(
                ValidationError,
                'Ensure this value has at most 512 characters'):
            # Capture the output just to reduce noise in the test
            # output - this would include output from
            # show_data_on_error otherwise.
            with capture_output() as (out, err):
                importer.import_from_export_json_data(data)


    def test_truncation_warn(self):
        long_name = ('Albert ' * 100).strip()
        input_json = '''
{{
    "persons": [
        {{
            "id": "a1b2",
            "name": "{0}"
        }}
    ]
}}
'''.format(long_name)
        data = json.loads(input_json)
        # With truncate='warn' the field should be truncated, but
        # print a warning to stderr:
        importer = PopItImporter(truncate='warn')
        with capture_output() as (out, err):
            importer.import_from_export_json_data(data)
        output = err.getvalue().strip()
        self.assertIn('Warning: truncating Albert', output)
        self.assertIn('Albert to a length of 512', output)
        person = models.Person.objects.get()
        max_length = person._meta.get_field('name').max_length
        truncated_name = long_name[:max_length]
        self.assertEqual(person.name, truncated_name)

    def test_dont_recreate_related_objects(self):
        input_json = '''
{
    "persons": [
        {
            "id": "a1b2",
            "name": "Alice",
            "identifiers": [
                {
                    "identifier": "123456789",
                    "scheme": "yournextmp-candidate"
                }
            ],
            "contact_details": [
                {
                    "contact_type": "twitter",
                    "label": "",
                    "note": "",
                    "value": "sometwitterusernameorother"
                }

            ],
            "links": [
                {
                    "note": "homepage",
                    "url": "http://example.com/alice"
                }
            ]
        }
    ]
}
'''
        data = json.loads(input_json)
        importer = PopItImporter()
        importer.import_from_export_json_data(data)
        self.assertEqual(models.Person.objects.count(), 1)
        original_person = models.Person.objects.get()
        self.assertEqual(original_person.name, "Alice")
        self.assertEqual(original_person.identifiers.count(), 2)
        original_identifier_a = original_person.identifiers.get(scheme='popit-person')
        original_identifier_b = original_person.identifiers.get(scheme='yournextmp-candidate')
        self.assertEqual(original_identifier_a.identifier, "a1b2")
        self.assertEqual(original_identifier_b.identifier, "123456789")
        self.assertEqual(original_person.contact_details.count(), 1)
        original_contact_detail = original_person.contact_details.get()

        # Now try importing again, and refetch those objects:
        importer = PopItImporter()
        importer.import_from_export_json_data(data)
        self.assertEqual(models.Person.objects.count(), 1)
        new_person = models.Person.objects.get()
        self.assertEqual(new_person.name, "Alice")
        self.assertEqual(new_person.identifiers.count(), 2)
        new_identifier_a = new_person.identifiers.get(scheme='popit-person')
        new_identifier_b = new_person.identifiers.get(scheme='yournextmp-candidate')
        self.assertEqual(new_identifier_a.identifier, "a1b2")
        self.assertEqual(new_identifier_b.identifier, "123456789")
        self.assertEqual(new_person.contact_details.count(), 1)
        new_contact_detail = new_person.contact_details.get()
        # Now check that these objects haven't changed ID:
        self.assertEqual(original_person.id, new_person.id)
        self.assertEqual(original_identifier_a.id, new_identifier_a.id)
        self.assertEqual(original_identifier_b.id, new_identifier_b.id)
        self.assertEqual(original_contact_detail.id, new_contact_detail.id)

    def test_organization_with_identifiers(self):
        input_json = '''
{
    "organizations": [
        {
            "id": "commons",
            "name": "House of Commons",
            "identifiers": [
                {
                    "scheme": "big-db-of-parliaments",
                    "identifier": "uk-commons"
                }
            ]
        }
    ]
}
'''
        data = json.loads(input_json)
        importer = PopItImporter()
        importer.import_from_export_json_data(data)
        self.assertEqual(models.Organization.objects.count(), 1)
        organization = models.Organization.objects.get()
        self.assertEqual(organization.name, "House of Commons")
        self.assertEqual(
            organization.identifiers.get(scheme='popit-organization').identifier,
            "commons"
        )
        self.assertEqual(
            organization.identifiers.get(scheme='big-db-of-parliaments').identifier,
            "uk-commons"
        )

    def test_organisation_with_inline_area(self):
        input_json = '''
{
    "organizations": [
        {
            "id": "commons",
            "name": "House of Commons",
            "area": {
                "id": "area-1",
                "name": "The United Kingdom of Great Britain and Northern Ireland",
                "identifier": "uk",
                "classification": "country"
            }
        }
    ]
}
'''
        data = json.loads(input_json)
        importer = PopItImporter()
        importer.import_from_export_json_data(data)
        self.assertEqual(models.Organization.objects.count(), 1)
        self.assertEqual(models.Area.objects.count(), 1)
        area = models.Area.objects.get()
        self.assertEqual(
            area.name,
            'The United Kingdom of Great Britain and Northern Ireland')
        self.assertEqual(area.identifier, 'uk')
        self.assertEqual(area.classification, 'country')

    def test_organisation_with_external_area(self):
        input_json = '''
{
    "organizations": [
        {
            "id": "commons",
            "name": "House of Commons",
            "area_id": "area-1"
        }
    ],
    "areas": [
        {
            "id": "area-1",
            "name": "The United Kingdom of Great Britain and Northern Ireland",
            "identifier": "uk",
            "classification": "country"
        }
    ]
}
'''
        data = json.loads(input_json)
        importer = PopItImporter()
        importer.import_from_export_json_data(data)
        self.assertEqual(models.Organization.objects.count(), 1)
        self.assertEqual(models.Area.objects.count(), 1)
        area = models.Area.objects.get()
        self.assertEqual(
            area.name,
            'The United Kingdom of Great Britain and Northern Ireland')
        self.assertEqual(area.identifier, 'uk')
        self.assertEqual(area.classification, 'country')

    def test_exception_from_inline_area_missing_id(self):
        input_json = '''
{
    "organizations": [
        {
            "id": "commons",
            "name": "House of Commons",
            "area": {
                "name": "The United Kingdom of Great Britain and Northern Ireland",
                "identifier": "uk",
                "classification": "country"
            }
        }
    ]
}
'''
        data = json.loads(input_json)
        importer = PopItImporter()
        with capture_output() as (out, err):
            with self.assertRaisesRegexp(
                    ValueError,
                    'Found inline area data, but with no "id" attribute'):
                importer.import_from_export_json_data(data)

    def test_organization_parent_relationship(self):
        input_json = '''
{
    "organizations": [
        {
            "id": "co",
            "name": "Cabinet Office",
            "parent_id": "cs"
        },
        {
            "id": "cs",
            "name": "Civil Service"
        }
    ]
}
'''
        data = json.loads(input_json)
        importer = PopItImporter()
        importer.import_from_export_json_data(data)
        self.assertEqual(models.Organization.objects.count(), 2)
        child = models.Organization.objects.get(name='Cabinet Office')
        parent = models.Organization.objects.get(name='Civil Service')
        self.assertEqual(child.parent, parent)

    def test_area_parent_relationship(self):
        input_json = '''
{
    "areas": [
        {
            "id": "subarea-1",
            "name": "Scotland",
            "identifier": "sco",
            "classification": "country",
            "parent_id": "area-1"
        },
        {
            "id": "area-1",
            "name": "United Kingdom",
            "identifier": "uk",
            "classification": "country"
        }
    ]
}
'''
        data = json.loads(input_json)
        importer = PopItImporter()
        importer.import_from_export_json_data(data)
        self.assertEqual(models.Area.objects.count(), 2)
        child = models.Area.objects.get(name='Scotland')
        parent = models.Area.objects.get(name='United Kingdom')
        self.assertEqual(child.parent, parent)

    def test_all_top_level_optional(self):
        # This just check that you don't get an exception when
        # importing empty Popolo JSON.
        input_json = '{}'
        data = json.loads(input_json)
        importer = PopItImporter()
        importer.import_from_export_json_data(data)

    def test_link_and_source_without_a_note(self):
        input_json = '''
{
    "persons": [
        {
            "id": "a1b2",
            "name": "Alice",
            "sources": [
               {
                   "url": "http://example.org/source-of-alice-data"
               }
            ],
            "links": [
               {
                   "url": "http://example.org/a-link-without-a-note"
               }
            ]
        }
    ]
}
'''
        data = json.loads(input_json)
        importer = PopItImporter()
        importer.import_from_export_json_data(data)
        self.assertEqual(models.Person.objects.count(), 1)
        person = models.Person.objects.get()
        self.assertEqual(person.name, "Alice")
        self.assertEqual(
            person.sources.get().url,
            "http://example.org/source-of-alice-data")
        self.assertEqual(
            person.links.get().url,
            "http://example.org/a-link-without-a-note")


class LegislativePeriodMembershipTests(TestCase):
    """Tests for a special case to provide defaults for membership dates"""

    def setUp(self):
        # This Input data extracted from:
        # https://cdn.rawgit.com/everypolitician/everypolitician-data/a46ef721903ad86a07af2abbebf469015e9b4367/data/UK/Commons/ep-popolo-v1.0.json
        # This is quite a useful sample of real data so we should
        # reuse this to test the rest of it is parsed properly (FIXME).
        self.input_json = u'''
{
    "persons": [
        {
            "birth_date": "1955-04-09",
            "gender": "male",
            "given_name": "Eric",
            "id": "0588816f-94b5-4397-88f6-f3fdca0f94f0",
            "identifiers": [
                {
                    "identifier": "Commons/member/386",
                    "scheme": "parliamentdotuk"
                }
            ],
            "links": [
                {
                    "note": "Wikipedia (en)",
                    "url": "https://en.wikipedia.org/wiki/Eric_Illsley"
                }
            ],
            "name": "Eric Illsley",
            "other_names": [
                {
                    "lang": "ja",
                    "name": "エリック・イルズリー",
                    "note": "multilingual"
                }
            ]
        },
        {
            "birth_date": "1971-05-23",
            "contact_details": [
                {
                    "type": "email",
                    "value": "robertsonbj@parliament.uk"
                },
                {
                    "type": "email",
                    "value": "george.osborne.mp@parliament.uk"
                },
                {
                    "type": "phone",
                    "value": "020 7219 8214"
                },
                {
                    "type": "twitter",
                    "value": "George_Osborne"
                }
            ],
            "email": "robertsonbj@parliament.uk",
            "gender": "male",
            "given_name": "George",
            "id": "008ca7b1-fd32-420f-b710-d49fe8e34b05",
            "name": "George Osborne",
            "sort_name": "Osborne, Mr George"
        }
    ],
    "memberships": [
        {
            "area_id": "uk.org.publicwhip/cons/22",
            "end_date": "2011-02-08",
            "legislative_period_id": "term/55",
            "on_behalf_of_id": "labour",
            "organization_id": "8bbf6031-aa59-4b0a-80b2-1cdc81e4047d",
            "person_id": "0588816f-94b5-4397-88f6-f3fdca0f94f0",
            "role": "member"
        },
        {
            "area_id": "uk.org.publicwhip/cons/572",
            "legislative_period_id": "term/56",
            "on_behalf_of_id": "conservative",
            "organization_id": "8bbf6031-aa59-4b0a-80b2-1cdc81e4047d",
            "person_id": "008ca7b1-fd32-420f-b710-d49fe8e34b05",
            "role": "member"
        }
    ],
    "events": [
        {
            "classification": "legislative period",
            "end_date": "2015-03-30",
            "id": "term/55",
            "name": "55th Parliament of the United Kingdom",
            "organization_id": "8bbf6031-aa59-4b0a-80b2-1cdc81e4047d",
            "start_date": "2010-05-06",
            "wikidata": "Q21084472"
        },
        {
            "classification": "legislative period",
            "id": "term/56",
            "name": "56th Parliament of the United Kingdom",
            "organization_id": "8bbf6031-aa59-4b0a-80b2-1cdc81e4047d",
            "start_date": "2015-05-08",
            "wikidata": "Q21084473"
        }
    ],
    "organizations": [
        {
            "classification": "legislature",
            "id": "8bbf6031-aa59-4b0a-80b2-1cdc81e4047d",
            "identifiers": [
                {
                    "identifier": "Q11005",
                    "scheme": "wikidata"
                }
            ],
            "name": "House of Commons",
            "seats": 650
        },
        {
            "classification": "party",
            "id": "labour",
            "identifiers": [
                {
                    "identifier": "Q9630",
                    "scheme": "wikidata"
                }
            ],
            "name": "Labour"
        },
        {
            "classification": "party",
            "id": "conservative",
            "identifiers": [
                {
                    "identifier": "Q9626",
                    "scheme": "wikidata"
                }
            ],
            "links": [
                {
                    "note": "website",
                    "url": "http://www.conservatives.com"
                }
            ],
            "name": "Conservative"
        }
    ]
}
        '''

    def test_membership_no_dates_but_some_in_legislative_period(self):
        data = json.loads(self.input_json)
        importer = PopItImporter()
        importer.import_from_export_json_data(data)
        self.assertEqual(models.Membership.objects.count(), 2)
        earlier, later = models.Membership.objects.order_by('start_date')
        self.assertEqual(earlier.start_date, '2010-05-06')
        self.assertEqual(earlier.end_date, '2011-02-08')
        self.assertEqual(later.start_date, '2015-05-08')
        self.assertEqual(later.end_date, '')
