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

from adjutant_moc import services
from adjutant_moc import settings

from adjutant.common import user_store

SERVICES = {}
for k, v in settings.MOC_CONF['services'].items():
    SERVICES[k] = services.Service(v['url'])


class Operation(object):
    def __init__(self):
        self.log = []
        self.completed_services = []

    @property
    def identity(self):
        return user_store.IdentityManager()

    @staticmethod
    def get_driver(service):
        return SERVICES[service]  # type: services.Service

    def commit(self, cache):
        try:
            self.perform(cache)
            for service in self.services:
                self.replicate(service, cache)
        except Exception as e:
            self.log.append('Error: %s' % str(e))
            self.rollback(cache)
            raise e

    def perform(self, cache):
        raise NotImplementedError

    def replicate(self, driver: services.Service, cache):
        raise NotImplementedError

    def rollback(self, cache):
        raise NotImplementedError
