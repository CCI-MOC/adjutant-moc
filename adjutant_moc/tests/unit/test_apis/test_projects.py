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


class TestCreateProject(base.TestBase):

    url = "/v1/moc/Projects"

    demo_data = {
        'project_name': 'demoproject1',
        'description': 'demodescription',
        'organization': 'Test Org',
        'moc_contact': 'Test Contact',
        'phone': '555 555 5555',
        'organization_role': 'dungeon master',
        'setup_network': True,
        'services': [],
    }

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

    def test_create_project(self):
        r = self.client.post(self.url, json.dumps(self.demo_data),
                             headers=self.get_headers_for(self.users[1]),
                             content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_202_ACCEPTED)

    def test_create_project_twice_fails(self):
        r = self.client.post(self.url, json.dumps(self.demo_data),
                             headers=self.get_headers_for(self.users[1]),
                             content_type='application/json')
        r = self.client.post(self.url, json.dumps(self.demo_data),
                             headers=self.get_headers_for(self.users[1]),
                             content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_409_CONFLICT)

    def test_create_project_unauthenticated_fails(self):
        r = self.client.post(self.url, json.dumps(self.demo_data),
                             content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_project_wrong_data_fails(self):
        wrong_data = {
            'project_name': 'demoproject1',
            'description': 'demodescription',
            'extraneous_field': 'nono'
        }
        r = self.client.post(self.url, json.dumps(wrong_data),
                             headers=self.get_headers_for(self.users[0]),
                             content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_project_already_exists_fails(self):
        self.assertIsNotNone(self.identity.get_project(self.projects[0].id))

        wrong_data = self.demo_data.copy()
        wrong_data['project_name'] = self.projects[0].name
        r = self.client.post(self.url, json.dumps(wrong_data),
                             headers=self.get_headers_for(self.users[1]),
                             content_type='application/json')
        self.assertIn('already exists', str(r.json()))
        self.assertEqual(r.status_code, status.HTTP_409_CONFLICT)

    def test_disable_apis_fails(self):
        r = self.client.post(
            '/v1/openstack/sign-up', json.dumps(self.demo_data),
            headers=self.get_headers_for(self.users[1]),
            content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)
