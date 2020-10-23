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

from unittest import mock

from adjutant.tasks import models as task_models
from adjutant.api import models as api_models
from adjutant.common.tests import fake_clients
from django.test import TestCase

from adjutant_moc.actions import mailing_list





class FakeProject(fake_clients.FakeProject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tags = []

    def add_tag(self, tag):
        self.tags.append(tag)

    def list_tags(self):
        return self.tags

    def delete(self):
        del(fake_clients.identity_cache["projects"][self.id])


class FakeMailman(mailing_list.Mailman):
    def __enter__(self):
        return self


def _role_from_id(instance, role):
    if isinstance(role, fake_clients.FakeRole):
        return role
    else:
        return instance.find_role(role)


def fakerole_to_dict(instance):
    return {
        'name': instance.name,
        'id': str(instance.id)
    }
fake_clients.FakeRole.to_dict = fakerole_to_dict


class TestBase(TestCase):

    def setUp(self) -> None:
        self.maxDiff = None
        self.identity = fake_clients.FakeManager()

        project_patcher = mock.patch(
            'adjutant.common.tests.fake_clients.FakeProject',
            FakeProject)
        identity_patcher = mock.patch(
            'adjutant.common.user_store.IdentityManager',
            fake_clients.FakeManager)
        mailman_patcher = mock.patch(
            'adjutant_moc.actions.mailing_list.Mailman',
            FakeMailman
        )
        role_patcher = mock.patch(
            'adjutant.common.tests.fake_clients.FakeManager._role_from_id',
            _role_from_id)
        role_to_dict_patcher = mock.patch(
            'adjutant.common.tests.fake_clients.FakeRole.to_dict',
            fakerole_to_dict)

        self.project_patcher = project_patcher.start()
        self.identity_patcher = identity_patcher.start()
        self.mailman_patcher = mailman_patcher.start()
        self.role_patcher = role_patcher.start()
        self.role_to_dict_patcher = role_to_dict_patcher.start()

        self.addCleanup(role_to_dict_patcher.stop)
        self.addCleanup(role_patcher.stop)
        self.addCleanup(mailman_patcher.stop)
        self.addCleanup(identity_patcher.stop)
        self.addCleanup(project_patcher.stop)

        self.default_domain_id = 'default'

    @staticmethod
    def get_headers_for(user, project=None, roles=''):
        return {
            'username': user.name,
            'email': user.name,
            'user_id': user.id,
            'user_domain_id': user.domain_id,
            'authenticated': True,
            'project_name': project.name if project else '',
            'project_id': project.id if project else '',
            'project_domain_id': project.domain_id if project else '',
            'roles': roles,
        }

    @classmethod
    def new_task(cls, user=None) -> task_models.Task:
        keystone_user = {}
        if user:
            keystone_user = cls.get_headers_for(user)

        return task_models.Task.objects.create(keystone_user=keystone_user)

    @staticmethod
    def get_last_token() -> api_models.Token:
        return api_models.Token.objects.last()

    @staticmethod
    def get_task():
        pass
