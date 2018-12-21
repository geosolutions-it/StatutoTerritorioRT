#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


from django.core.management.base import (
    BaseCommand, CommandError
)
from strt_users.models import (
    Organization, OrganizationType, MembershipType
)


class Command(BaseCommand):

    help = 'Create models for tests'

    organizations = [
        {
            'code': 'RT',
            'name': 'Toscana',
            'type': {
                'code': 'R',
                'name': 'Regione'
            }
        },
        {
            'code': 'FI',
            'name': 'Firenze',
            'type': {
                'code': 'C',
                'name': 'Comune'
            }
        },
        {
            'code': 'LU',
            'name': 'Lucca',
            'type': {
                'code': 'C',
                'name': 'Comune'
            }
        },
        {
            'code': 'PI',
            'name': 'Pisa',
            'type': {
                'code': 'C',
                'name': 'Comune'
            }
        }
    ]

    membership_types = [
        {
            'code': 'RUP',
            'name': 'Responsabile Unico del Procedimento',
            'org_type': 'C'
        },
        {
            'code': 'RUP',
            'name': 'Responsabile Unico del Procedimento',
            'org_type': 'R'
        },
        {
            'code': 'IVAS',
            'name': 'Ispettore VAS',
            'org_type': 'R'
        },
        {
            'code': 'IPIT',
            'name': 'Ispettore PIT',
            'org_type': 'R'
        },
        {
            'code': 'OP',
            'name': 'Operatore',
            'org_type': 'C'
        },
        {
            'code': 'RI',
            'name': 'Responsabile ISIDE',
            'org_type': 'C'
        },
        {
            'code': 'RI',
            'name': 'Responsabile ISIDE',
            'org_type': 'R'
        }
    ]

    def handle(self, *args, **options):

        try:

            for org in self.organizations:

                org_type, created = OrganizationType._default_manager.get_or_create(
                    code=org['type']['code'],
                    name=org['type']['name'],
                )
                Organization._default_manager.get_or_create(
                    code=org['code'],
                    name=org['name'],
                    type=org_type
                )

            for mt in self.membership_types:

                membership_type, created = MembershipType._default_manager.get_or_create(
                    code=mt['code'],
                    organization_type=mt['org_type']
                )
                if created:
                    membership_type.name = mt["name"]
                    membership_type.description = f'{mt["name"]} per l\'ente {org_type.name}'
                    membership_type.save()

        except Exception as e:
            raise CommandError(e)

        self.stdout.write(self.style.SUCCESS('Successfully created models'))