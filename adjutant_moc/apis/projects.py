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

from confspirator import groups as config_groups
from confspirator import fields as config_fields
from adjutant.api import utils

from adjutant_moc.apis import base


class MocProjects(base.MocBaseApi):
    """
    API Endpoint for applying, or listing accessible projects.
    """

    url = r'^moc/Projects/?$'
    task_type = 'moc_create_project'

    config_group = config_groups.DynamicNameConfigGroup(
        children=[
            config_fields.BoolConfig(
                'create_default_network',
                help_text='Always create default network.',
                default=True,
                sample_default=True,
            ),
            config_fields.StrConfig(
                'region',
                help_text='Region for creating default network and quota.',
                default='RegionOne',
                sample_default='RegionOne'
            ),
            config_fields.StrConfig(
                "project_domain_id",
                help_text="Domain id for projects.",
                default="default",
                sample_default="Default"
            ),
        ]
    )

    @utils.authenticated
    def post(self, request, format=None):
        request.data['email'] = request.keystone_user['username']
        request.data['region'] = self.config['region']
        request.data['setup_network'] = self.config['create_default_network']
        request.data['domain_id'] = self.config['project_domain_id']

        project = self.identity.find_project(
            request.data['project_name'], 'default')
        if project:
            message = ('Project %s already exists.'
                       % request.data['project_name'])
            self.logger.info(message)
            return self.response_error(message, 409)

        return self.create_task(request)

    @utils.authenticated
    def get(self, request, format=None):
        # List other projects that a user has access to, or has applied for.
        pass


class MocProjectServices(base.MocBaseApi):
    """
    API Endpoint for listing and applying for more services to a project.
    """

    url = r'^moc/Services/?$'

    @utils.authenticated
    def get(self, request, format=None):
        # List other projects that a user has access to, or has applied for.
        pass
