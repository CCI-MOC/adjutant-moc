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

import uuid

from adjutant.common.tests import fake_clients

from adjutant_moc.tests import base
from adjutant_moc.actions import users


class UserActionTests(base.TestBase):

    token_confirm = {'confirm': True}

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

    def test_invite_user(self):
        task = self.new_task(self.users[1])

        data = {
            'email': self.users[0].name,
            'project_id': self.projects[0].id,
            'roles': ['member']
        }
        action = users.MocInviteUserAction(data, task=task, order=1)

        action.prepare()
        self.assertEqual(action.valid, True)
        action.approve()
        self.assertEqual(action.valid, True)

        token = self.token_confirm.copy()
        token['user'] = self.get_headers_for(self.users[0])
        action.submit(token)

        roles = self.identity._get_roles_as_names(
            self.users[0], self.projects[0])
        self.assertEqual(sorted(roles), sorted(data['roles']))
