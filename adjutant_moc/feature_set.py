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

from adjutant import feature_set

from adjutant_moc import actions as moc_actions
from adjutant_moc import apis as moc_apis
from adjutant_moc import tasks as moc_tasks


class MocOnboardingFeatureSet(feature_set.BaseFeatureSet):
    actions = [
        moc_actions.mailing_list.MailingListSubscribeAction,
        moc_actions.projects.MocNewProjectAction,
        moc_actions.users.MocInviteUserAction,
    ]

    tasks = [
        moc_tasks.projects.MocCreateProject,
        moc_tasks.projects.MocInviteUser,
    ]

    delegate_apis = [
        moc_apis.healthcheck.MocHealthCheck,
        moc_apis.projects.MocProjects,
        moc_apis.users.MocUsers,
        moc_apis.users.MocUsersDetail,
        moc_apis.users.MocAcceptInvite,
        moc_apis.roles.MocRoles,
    ]

    notification_handlers = [
    ]
