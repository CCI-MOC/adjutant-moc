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
from adjutant.api.v1 import openstack as adjutant_apis
from rest_framework.response import Response
from adjutant.common import user_store
from adjutant.api import models
from adjutant.api import utils
from adjutant.config import CONF

from adjutant_moc.apis import base


class MocUsers(adjutant_apis.UserList):
    """
    API Endpoint for inviting or listing users on current project.
    """
    url = r'^moc/Users/?$'
    task_type = "moc_invite_user"

    @utils.mod_or_admin
    def get(self, request):
        # FIXME(knikolla): This is mostly a copy of the method from the base
        # class, the only thing I had to change was to rename the name of the
        # task that invites people so that we can show those in the invited
        # users tab.
        class_conf = self.config
        blacklisted_roles = class_conf.blacklisted_roles

        user_list = []
        id_manager = user_store.IdentityManager()
        project_id = request.keystone_user["project_id"]
        project = id_manager.get_project(project_id)

        can_manage_roles = id_manager.get_manageable_roles(
            request.keystone_user["roles"]
        )

        active_emails = set()
        for user in id_manager.list_users(project):
            skip = False
            roles = []
            for role in user.roles:
                if role.name in blacklisted_roles:
                    skip = True
                    continue
                roles.append(role.name)
            if skip:
                continue
            inherited_roles = []
            for role in user.inherited_roles:
                if role.name in blacklisted_roles:
                    skip = True
                    continue
                inherited_roles.append(role.name)
            if skip:
                continue

            email = getattr(user, "email", "")
            enabled = user.enabled
            user_status = "Active" if enabled else "Account Disabled"
            active_emails.add(email)
            user_list.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "email": email,
                    "roles": roles,
                    "inherited_roles": inherited_roles,
                    "cohort": "Member",
                    "status": user_status,
                    "manageable": set(can_manage_roles).issuperset(roles),
                }
            )

        for user in id_manager.list_inherited_users(project):
            skip = False
            roles = []
            for role in user.roles:
                if role.name in blacklisted_roles:
                    skip = True
                    continue
                roles.append(role.name)
            if skip:
                continue

            email = getattr(user, "email", "")
            enabled = user.enabled
            user_status = "Active" if enabled else "Account Disabled"
            user_list.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "email": email,
                    "roles": roles,
                    "inherited_roles": [],
                    "cohort": "Inherited",
                    "status": user_status,
                    "manageable": False,
                }
            )

        # Get my active tasks for this project:
        project_tasks = models.Task.objects.filter(
            project_id=project_id,
            task_type="moc_invite_user",
            completed=0,
            cancelled=0,
        )

        registrations = []
        for task in project_tasks:
            status = "Invited"
            for token in task.tokens:
                if token.expired:
                    status = "Expired"

            for notification in task.notifications:
                if notification.error:
                    status = "Failed"

            for action in task.actions:
                if not action.valid:
                    status = "Invalid"

            task_data = {}
            for action in task.actions:
                task_data.update(action.action_data)

            registrations.append(
                {"uuid": task.uuid, "task_data": task_data, "status": status}
            )

        for task in registrations:
            # NOTE(adriant): commenting out for now as it causes more confusion
            # than it helps. May uncomment once different duplication checking
            # measures are in place.
            # if task['task_data']['email'] not in active_emails:
            user = {
                "id": task["uuid"],
                "name": task["task_data"]["email"],
                "email": task["task_data"]["email"],
                "roles": task["task_data"]["roles"],
                "cohort": "Invited",
                "status": task["status"],
            }
            if not CONF.identity.username_is_email:
                user["name"] = task["task_data"]["username"]

            user_list.append(user)

        return Response({"users": user_list})


class MocUsersDetail(adjutant_apis.UserDetail):
    """
    API Endpoint for interacting with a specific user.
    """

    url = r'^moc/Users/(?P<user_id>\w+)/?$'

    @utils.mod_or_admin
    def patch(self, request, format=None):
        # Edit Roles
        pass


class MocAcceptInvite(base.MocBaseApi):

    url = r'^moc/Invitations/(?P<token_id>\w+)/?$'

    @utils.authenticated
    def post(self, request, token_id, format=None):
        try:
            token = models.Token.objects.get(token=token_id)
            if token.expires < timezone.now():
                token.delete()
                token = models.Token.objects.get(token=token_id)
        except models.Token.DoesNotExist:
            return self.response_error(
                'This token does not exist or has expired.', 404)

        if not token.task.task_type == 'moc_invite_user':
            return self.response_error(
                'This token is not for a project invitation.', 400)

        if 'user' in request.data:
            return self.response_error(
                'User data is not allowed in token.', 400)

        # Check that the user matches the invited user.
        valid_user = False
        for action in token.task.actions:
            if action.action_name == 'MocInviteUserAction':
                if (action.action_data['email']
                        == request.keystone_user['username']):
                    valid_user = True
        if not valid_user:
            return self.response_error(
                'Authenticated user does not match invited user.', 400)

        # This makes it so that only here can we inject authentication data.
        request.data['user'] = request.keystone_user
        self.task_manager.submit(token.task, request.data)

        return Response({'notes': ["Token submitted successfully."]},
                        status=200)
