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

import json
import uuid

from adjutant import config
from rest_framework import status

from adjutant_moc import services
from adjutant_moc.tests.functional import base

CONF = config.CONF


class TestCreateProject(base.FunctionalTestBase):

    def test_create_project_no_network_no_services(self):
        user = self._create_user()
        self._signup(user, [])

    def test_create_project_no_network_openshift_service(self):
        user = self._create_user()
        p = self._signup(user, ['staging-openshift'])

        openshift = services.Service(
            'https://acct-mgt-acct-mgt.s-apps.osh.massopen.cloud')
        openshift.get_project(p.id)
        openshift.get_user(user.name)
        openshift.get_role(p.id, user.name, 'project_admin')
        openshift.get_role(p.id, user.name, 'member')

        openshift.delete_project(p.id)
        openshift.delete_user(user.name)
