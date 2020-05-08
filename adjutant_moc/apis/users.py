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
from adjutant.api import models
from adjutant.api import utils
from adjutant.api.v1 import openstack as adjutant_apis
from rest_framework.response import Response

from adjutant_moc.apis import base


class MocUsers(adjutant_apis.UserList):
    """
    API Endpoint for inviting or listing users on current project.
    """
    url = r'^moc/Users/?$'
    task_type = "moc_invite_user"


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
