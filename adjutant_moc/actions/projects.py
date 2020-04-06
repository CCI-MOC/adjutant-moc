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

from adjutant.common import user_store
from adjutant.actions.v1 import resources as resource_actions
from confspirator import groups as config_groups
from confspirator import fields as config_fields

from adjutant_moc.actions import base, operations
from adjutant_moc.actions import serializers


class MocNewProjectAction(base.MocBaseAction):
    """Creates a new project for the current authenticated user."""

    required = [
        'project_name',
        'description',
        'domain_id',

        # TODO(knikolla): It should be possible to fetch these from
        # SSO once we support OAuth 2.0 access tokens.
        'organization',
        'organization_role',

        'services',

        'phone',
        'moc_contact',
    ]

    serializer = serializers.MocNewProjectSerializer

    config_group = config_groups.DynamicNameConfigGroup(
        children=[
            config_fields.ListConfig(
                "default_roles",
                help_text="Roles to be given on project to the creating user.",
                default=["member", "project_admin"],
                sample_default=["member", "project_admin"]
            ),
            config_fields.ListConfig(
                "enabled_services",
                help_text="Other services configured in the cloud.",
                default=['openshift'],
            ),
        ],
    )

    def _validate_project_name(self):
        # Make sure project id doesn't exist.
        project = self.identity.find_project(self.project_name,
                                             self.domain_id)
        if project:
            return False
        return True

    def _validate_services(self):
        for service in self.services:
            if service not in self.config.enabled_services:
                return False
        return True

    def _get_email(self):
        return self.action.task.keystone_user['username']

    def write_to_approve_journal(self):
        user_ref = self._get_user()
        project_ref = {
            'name': self.project_name,
            'domain_id': self.domain_id,
            'description': self.description,
            'organization': self.organization,
            'owner': self._get_email(),
        }
        self.approve_journal.append(operations.CreateProjectOperation(
            self.services, project_ref))
        self.approve_journal.append(operations.AddUserToProjectOperation(
            self.services, user_ref, project_ref, self.config.default_roles))

    def write_to_submit_journal(self, token_data):
        pass
