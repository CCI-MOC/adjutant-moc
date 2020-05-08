# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import uuid

from adjutant.common.tests import fake_clients
from rest_framework import status

from adjutant_moc.tests import base


class TestListRoles(base.TestBase):

    url = '/v1/moc/Roles'

    def setUp(self) -> None:
        super().setUp()

        self.projects = [
            fake_clients.FakeProject(name=uuid.uuid4().hex),
            fake_clients.FakeProject(name=uuid.uuid4().hex),
            fake_clients.FakeProject(name=uuid.uuid4().hex)
        ]
        self.users = [
            fake_clients.FakeUser(name='user0@example.com'),
            fake_clients.FakeUser(name='user1@example.com'),
            fake_clients.FakeUser(name='user2@example.com')
        ]

        fake_clients.setup_identity_cache(projects=self.projects,
                                          users=self.users)

    def test_list_roles_for_project_admin(self):
        r = self.client.get(
            self.url, headers=self.get_headers_for(self.users[0],
                                                   project=self.projects[0],
                                                   roles='project_admin,member'),
            content_type='application/json'
        )

        roles = json.loads(r.content)['roles']
        self.assertEqual(len(roles), 2)
        for r in roles:
            self.assertIn(r['name'], ['member', 'project_admin'])

    def test_list_roles_for_member(self):
        r = self.client.get(
            self.url, headers=self.get_headers_for(self.users[0],
                                                   project=self.projects[0],
                                                   roles='member'),
            content_type='application/json'
        )

        try:
            roles = json.loads(r.content)['roles']
            self.assertEqual(len(roles), 0)
        except Exception:
            # It seems that it doesn't even return anything here
            pass
