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
from rest_framework.response import Response
from adjutant.api import utils

from adjutant_moc.apis import base
from adjutant_moc.actions import mailing_list

from adjutant.config import CONF


class MocHealthCheck(base.MocBaseApi):
    """
    API Endpoint for checking the health of Adjutant.
    """
    url = r'^moc/HealthCheck/?$'

    config_group = config_groups.DynamicNameConfigGroup(
        children=[
            config_fields.BoolConfig(
                'check_mailing_list',
                help_text='Check SSH connection to mailing list server.',
                default=True,
                sample_default=True,
            ),
        ]
    )

    def get(self, request, format=None):
        errors = {
            'MailingList': self._check_mailing_list()
        }

        return Response({'errors': errors})

    def _get_action_defaults(self, action):
        return CONF.workflow.action_defaults.get(action)

    def _check_mailing_list(self):
        config = self._get_action_defaults('MailingListSubscribeAction')
        try:
            with mailing_list.Mailman(config.host,
                                      config.port,
                                      config.user,
                                      config.private_key) as mailman:
                mailman.is_already_subscribed('test@example.com', config.list)
                return []
        except Exception as e:
            return [str(e)]
