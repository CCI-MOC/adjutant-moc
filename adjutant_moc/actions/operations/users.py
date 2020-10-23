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

from adjutant_moc.actions.operations.core import Operation


class AddUserToProjectOperation(Operation):
    def __init__(self, services, user_ref, project_ref, roles):
        super().__init__()

        self.user_ref = user_ref
        self.project_ref = project_ref
        self.role_names = roles

        self.user = None
        self.project = None
        self.services = services

    def _get_user(self):
        if self.user_ref.get('user_id'):
            self.log.append(
                'User id provided. Getting user by id %s' % self.user_ref['user_id']
            )
            self.user = self.identity.get_user(self.user_ref['user_id'])
            return

        self.log.append(
            'Looking for username %s in domain %s' % (self.user_ref['username'],
                                                      self.user_ref['user_domain_id'])
        )
        self.user = self.identity.find_user(self.user_ref['username'],
                                            self.user_ref['user_domain_id'])
        if not self.user:
            self.log.append('User not found.')

    def perform(self, cache):
        self.project = self.identity.find_project(
            self.project_ref['name'], self.project_ref['domain_id'])
        self._get_user()
        self.roles = [self.identity.find_role(r) for r in self.role_names]

        for role in self.roles:
            self.identity.add_user_role(self.user, role, self.project)

    def replicate(self, service, cache):
        for service in self.services:
            # Currently, the microservice doesn't throw a bad request if the
            # user already exists.
            self.get_driver(service).create_user(self.user_ref['username'])
            for role in self.role_names:
                self.get_driver(service).add_role(
                    self.user_ref['username'], self.project.id, role)
            self.completed_services.append(service)

    def rollback(self, cache):
        for service in self.completed_services:
            for role in self.role_names:
                self.get_driver(service).delete_role(
                    self.user_ref['username'], self.project.id, role)

        if self.user:
            for role in self.roles:
                self.identity.remove_user_role(self.user, role, self.project)
