# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from rest_framework import serializers
from adjutant.actions.v1 import serializers as adjutant_serializers


class MocNewProjectSerializer(
    adjutant_serializers.NewProjectSerializer
):
    organization = serializers.CharField(max_length=64)
    organization_role = serializers.CharField(max_length=64)
    phone = serializers.CharField(max_length=64)
    moc_contact = serializers.CharField(max_length=64)
    services = serializers.ListField()


class MocInviteUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    project_id = serializers.CharField(max_length=64)
    roles = serializers.MultipleChoiceField(
        default=set, choices=set(['member', 'project_admin']))


class MailingListSubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()
