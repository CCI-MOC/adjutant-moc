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

from adjutant.api import models as api_models
from rest_framework import status
from django.test import TestCase
from adjutant.common import user_store
from adjutant.config import CONF


class FunctionalTestBase(TestCase):

    def setUp(self) -> None:
        super().setUp()
        for key in ['kaizen', 'massopen', '.cloud', '.com']:
            if key in CONF.identity.auth.auth_url:
                self.skipTest('Detected possible run on production systems.')

        self.identity = user_store.IdentityManager()
        self.ks_client = self.identity.ks_client

    def _create_user(self):
        email = '%s@example.com' % uuid.uuid4().hex
        user = self.ks_client.users.create(name=email,
                                           domain='default',
                                           password=uuid.uuid4().hex,
                                           email=email,
                                           enabled=True)
        self.addCleanup(user.delete)
        return user

    def _create_project(self):
        project = self.ks_client.projects.create(name=uuid.uuid4().hex,
                                                 domain='default')
        self.addCleanup(project.delete)
        return project

    def _signup(self, user, services):
        project_request = {
            'project_name': uuid.uuid4().hex,
            'description': uuid.uuid4().hex,
            'organization': uuid.uuid4().hex,
            'moc_contact': uuid.uuid4().hex,
            'phone': uuid.uuid4().hex,
            'organization_role': uuid.uuid4().hex,
            'setup_network': False,
            'services': services,
        }
        r = self.client.post('/v1/moc/Projects', json.dumps(project_request),
                             headers=self.get_headers_for(user),
                             content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_202_ACCEPTED)
        task = self.find_task_by_user(user.name)

        r = self.client.post('/v1/tasks/%s' % task['uuid'],
                             json.dumps({'approved': True}),
                             headers=self.get_admin_headers(),
                             content_type='application/json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        p = self.ks_client.projects.find(name=project_request['project_name'],
                                         domain='default')
        self.addCleanup(p.delete)
        return p

    @staticmethod
    def get_headers_for(user, project=None, roles=''):
        return {
            'username': user.name,
            'email': user.name,
            'user_id': user.id,
            'user_domain_id': user.domain_id,
            'authenticated': True,
            'project_name': project.name if project else '',
            'project_id': project.id if project else '',
            'project_domain_id': project.domain_id if project else '',
            'roles': roles,
        }

    def get_admin_headers(self):
        u = self.ks_client.users.list(name='admin', domain='default')[0]
        p = self.ks_client.projects.list(name='admin', domain='default')[0]
        return self.get_headers_for(u, p, 'admin')

    def find_task_by_user(self, username):
        r = self.client.get('/v1/tasks',
                            headers=self.get_admin_headers(),
                            content_type='application/json').json()
        for task in r['tasks']:
            if task['keystone_user']['username'] == username:
                return task

    @staticmethod
    def get_last_token() -> api_models.Token:
        return api_models.Token.objects.last()
