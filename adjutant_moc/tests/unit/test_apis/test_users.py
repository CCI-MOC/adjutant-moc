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


class TestUsers(base.TestBase):

    url = '/v1/moc/Users'

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

    def test_invite_and_accept(self):
        invite = {
            'email': self.users[1].name,
            'roles': ['member', 'project_admin']
        }
        r = self.client.post(
            self.url, json.dumps(invite),
            headers=self.get_headers_for(self.users[0],
                                         project=self.projects[0],
                                         roles='project_admin'),
            content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_202_ACCEPTED)

        token = self.get_last_token().token
        r = self.client.post('/v1/moc/Invitations/%s' % token,
                             json.dumps({'confirm': True}),
                             headers=self.get_headers_for(self.users[1]),
                             content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_invite_and_accept_wrong_endpoint(self):
        invite = {
            'email': self.users[1].name,
            'roles': ['member', 'project_admin']
        }
        r = self.client.post(
            self.url, json.dumps(invite),
            headers=self.get_headers_for(self.users[0],
                                         project=self.projects[0],
                                         roles='project_admin'),
            content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_202_ACCEPTED)

        token = self.get_last_token().token
        r = self.client.post('/v1/tokens/%s' % token,
                             json.dumps({'confirm': True}),
                             headers=self.get_headers_for(self.users[1]),
                             content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invite_and_accept_wrong_user_fails(self):
        invite = {
            'email': self.users[1].name,
            'roles': ['member', 'project_admin']
        }
        r = self.client.post(
            self.url, json.dumps(invite),
            headers=self.get_headers_for(self.users[0],
                                         project=self.projects[0],
                                         roles='project_admin'),
            content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_202_ACCEPTED)

        token = self.get_last_token().token
        r = self.client.post('/v1/moc/Invitations/%s' % token,
                             json.dumps({'confirm': True}),
                             headers=self.get_headers_for(self.users[2]),
                             content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invite_wrong_token_404(self):
        invite = {
            'email': self.users[1].name,
            'roles': ['member', 'project_admin']
        }
        r = self.client.post(
            self.url, json.dumps(invite),
            headers=self.get_headers_for(self.users[0],
                                         project=self.projects[0],
                                         roles='project_admin'),
            content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_202_ACCEPTED)

        r = self.client.post('/v1/moc/Invitations/12345',
                             json.dumps({'confirm': True}),
                             headers=self.get_headers_for(self.users[1]),
                             content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_invite_twice(self):
        invite = {
            'email': self.users[1].name,
            'roles': ['member', 'project_admin']
        }
        for _ in [0, 1]:
            r = self.client.post(
                self.url, json.dumps(invite),
                headers=self.get_headers_for(self.users[0],
                                             project=self.projects[0],
                                             roles='project_admin'),
                content_type='application/json')
            self.assertEqual(r.status_code, status.HTTP_202_ACCEPTED)

    def test_invite_project_admin_to_member(self):
        invite = {
            'email': self.users[1].name,
            'roles': ['member']
        }
        r = self.client.post(
            self.url, json.dumps(invite),
            headers=self.get_headers_for(self.users[0],
                                         project=self.projects[0],
                                         roles='project_admin'),
            content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_202_ACCEPTED)

    def test_invite_project_admin_to_project_admin(self):
        invite = {
            'email': self.users[1].name,
            'roles': ['project_admin']
        }
        r = self.client.post(
            self.url, json.dumps(invite),
            headers=self.get_headers_for(self.users[0],
                                         project=self.projects[0],
                                         roles='project_admin'),
            content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_202_ACCEPTED)

    def test_invite_wrong_role(self):
        invite = {
            'email': self.users[1].name,
            'roles': ['blabla']
        }
        r = self.client.post(
            self.url, json.dumps(invite),
            headers=self.get_headers_for(self.users[0],
                                         project=self.projects[0],
                                         roles='project_admin'),
            content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invite_member_fails(self):
        invite = {
            'email': self.users[1].name,
            'roles': ['member']
        }
        r = self.client.post(
            self.url, json.dumps(invite),
            headers=self.get_headers_for(self.users[0],
                                         project=self.projects[0],
                                         roles='member'),
            content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

        invite = {
            'email': self.users[1].name,
            'roles': ['project_admin']
        }
        r = self.client.post(
            self.url, json.dumps(invite),
            headers=self.get_headers_for(self.users[0],
                                         project=self.projects[0],
                                         roles='member'),
            content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
