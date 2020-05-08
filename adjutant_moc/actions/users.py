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

from adjutant_moc.actions import base, operations
from adjutant_moc.actions import serializers


class MocInviteUserAction(base.MocBaseAction):

    required = [
        'email',
        'project_id',
        'roles',
    ]

    serializer = serializers.MocInviteUserSerializer

    config_group = config_groups.DynamicNameConfigGroup(
        children=[config_fields.StrConfig(
            "user_domain_id",
            help_text="Domain to create projects in.",
            default="default",
            sample_default="Default")]
    )

    def _get_email(self):
        """This is the email where the invitation will be sent."""
        return self.email

    def _prepare(self):
        if not self._validate():
            self.add_note('Validation failed at _prepare')
            return

        self.action.auto_approve = True
        self.action.state = "pending"
        self.action.need_token = True
        self.set_token_fields(["confirm", "user"])

    def validate_token(self, token_data):
        if not self.valid or not token_data.get('confirm'):
            self.add_note('Invitation not valid or not accepted.')
            return False
        return True

    def write_to_approve_journal(self):
        pass

    def write_to_submit_journal(self, token_data):
        project = self.leader_identity.get_project(self.project_id)
        project_ref = {'name': project.name,
                       'domain_id': project.domain_id}
        services = self.find_services_for_project(project)
        self.submit_journal.append(operations.AddUserToProjectOperation(
            services, token_data['user'], project_ref, self.roles))
