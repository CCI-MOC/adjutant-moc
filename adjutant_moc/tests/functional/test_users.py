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

from adjutant import config
from rest_framework import status

from adjutant_moc import services
from adjutant_moc.tests.functional import base

CONF = config.CONF


class TestUsers(base.FunctionalTestBase):

    def test_user_list_and_invite(self):
        user = self._create_user()
        invitee = self._create_user()
        project = self._signup(user, [])

        u = self.client.get('/v1/moc/Users',
                            headers=self.get_headers_for(
                                user, project, 'project_admin'),
                            content_type='application/json').json()

        self.assertEqual(len(u['users']), 1)
        self.assertEqual(u['users'][0]['id'], user.id)

        invite = {'email': invitee.name, 'roles': ['member']}
        r = self.client.post('/v1/moc/Users', json.dumps(invite),
                             headers=self.get_headers_for(
                                 user, project, 'project_admin'),
                             content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_202_ACCEPTED)

        token = self.get_last_token().token
        r = self.client.post('/v1/moc/Invitations/%s' % token,
                             json.dumps({'confirm': True}),
                             headers=self.get_headers_for(invitee),
                             content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        u = self.client.get('/v1/moc/Users',
                            headers=self.get_headers_for(
                                user, project, 'project_admin'),
                            content_type='application/json').json()
        self.assertEqual(len(u['users']), 2)

    def test_user_list_and_invite_services(self):
        user = self._create_user()
        invitee = self._create_user()
        project = self._signup(user, ['staging-openshift'])

        invite = {'email': invitee.name, 'roles': ['member']}
        r = self.client.post('/v1/moc/Users', json.dumps(invite),
                             headers=self.get_headers_for(
                                 user, project, 'project_admin'),
                             content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_202_ACCEPTED)

        token = self.get_last_token().token
        r = self.client.post('/v1/moc/Invitations/%s' % token,
                             json.dumps({'confirm': True}),
                             headers=self.get_headers_for(invitee),
                             content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        u = self.client.get('/v1/moc/Users',
                            headers=self.get_headers_for(
                                user, project, 'project_admin'),
                            content_type='application/json').json()
        self.assertEqual(len(u['users']), 2)

        openshift = services.Service(
            'https://acct-mgt-acct-mgt.s-apps.osh.massopen.cloud')

        openshift.get_user(invitee.name)
        openshift.get_role(project.id, invitee.name, 'member')

        openshift.delete_project(project.id)
        openshift.delete_user(user.name)
        openshift.delete_user(invitee.name)
