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
        self.roles = roles

        self.user = None
        self.project = None
        self.services = services
        self.completed_services = None

    def perform(self):
        self.project = self.identity.find_project(
            self.project_ref['name'], self.project_ref['domain_id'])
        self.user = self.identity.find_user(
            self.user_ref['username'], self.user_ref['user_domain_id'])
        for role in self.roles:
            self.identity.add_user_role(self.user, role, self.project)

    def replicate(self, service):
        for service in self.services:
            # Currently, the microservice doesn't throw a bad request if the
            # user already exists.
            self.get_driver(service).create_user(self.user_ref['username'])
            for role in self.roles:
                self.get_driver(service).add_role(
                    self.user_ref['username'], self.project.id, role)
            self.completed_services.append(service)

    def rollback(self):
        for service in self.completed_services:
            for role in self.roles:
                self.get_driver(service).delete_role(
                    self.user_ref['username'], self.project.id, role)

        if self.user:
            for role in self.roles:
                self.identity.remove_user_role(self.user, role, self.project)
