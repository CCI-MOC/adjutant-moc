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

from adjutant.common.tests import fake_clients

from adjutant_moc.tests import base
from adjutant_moc.actions import projects


class ProjectActionTests(base.TestBase):

    demo_data = {
        'project_name': 'test_project',
        'description': 'demodescription',
        'organization': 'Test Org',
        'moc_contact': 'Test Contact',
        'phone': '555 555 5555',
        'organization_role': 'dungeon master',
        'setup_network': True,
        'domain_id': 'default',
        'services': [],
    }

    def setUp(self) -> None:
        super().setUp()

        self.users = [
            fake_clients.FakeUser(name='user0@example.com')
        ]
        fake_clients.setup_identity_cache(users=self.users)

    def test_new_project(self):
        task = self.new_task(self.users[0])
        action = projects.MocNewProjectAction(
            self.demo_data, task=task, order=1)

        action.prepare()
        self.assertEqual(action.valid, True)

        action.approve()
        self.assertEqual(action.valid, True)

        project = self.identity.find_project(self.demo_data['project_name'],
                                             self.default_domain_id)
        self.assertEqual(project.name, 'test_project')

        roles = self.identity._get_roles_as_names(self.users[0], project)
        self.assertEqual(
            sorted(roles),
            sorted(['member', 'project_admin']))
