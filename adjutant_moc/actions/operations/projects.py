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

from django.utils import timezone

from adjutant_moc.actions.operations.core import Operation


class CreateProjectOperation(Operation):

    def __init__(self, services, project_ref):
        super().__init__()
        self.project_ref = project_ref
        self.services = services
        self.project = None

    def perform(self, cache):
        self.project = self.identity.create_project(
            project_name=self.project_ref['name'],
            domain=self.project_ref['domain_id'],
            created_on=timezone.now(),
            description=self.project_ref['description']
        )
        cache['project_id'] = self.project.id
        self.log.append(
            'Project %s created on leader.' % str(self.project_ref))

    def replicate(self, service, cache):
        self.get_driver(service).create_project(self.project.id,
                                                self.project_ref['name'])
        self.project.add_tag('service:%s' % service)
        self.log.append('Project %s created on %s' % (str(self.project_ref),
                                                      service))
        self.completed_services.append(service)

    def rollback(self, cache):
        if not self.project:
            self.log.append(
                'Leader project not created, nothing to rollback.')
            return

        for service in self.completed_services:
            try:
                self.get_driver(service).delete_project(self.project_id)
            except Exception as e:
                self.log.append(
                    'Error deleting on %s: %s' % (service, str(e.msg)))

        # Finally, delete the Leader project
        self.project.delete()
