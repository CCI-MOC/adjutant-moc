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

from adjutant.common.tests import fake_clients
import paramiko

from adjutant_moc.tests import base
from adjutant_moc.actions import mailing_list


class MailingListActionTests(base.TestBase):

    data = {'email': 'user0@example.com'}

    def setUp(self) -> None:
        super().setUp()

        self.users = [
            fake_clients.FakeUser(name='user0@example.com')
        ]
        fake_clients.setup_identity_cache(users=self.users)

    def test_mailing_list_subscribe(self):
        task = self.new_task(self.users[0])
        action = mailing_list.MailingListSubscribeAction(
            self.data, task=task, order=1)

        action.prepare()
        with mock.patch.object(
                mailing_list.Mailman,
                '_execute',
                return_value=['blabla@example.com']) as mailman:
            action.approve()
            mailman.assert_has_calls([
                mock.call('/usr/lib/mailman/bin/list_members kaizen-users'),
                mock.call('echo user0@example.com | /usr/lib/mailman/bin/add_members -r - kaizen-users')  # noqa
            ])

        self.assertEqual('complete', action.action.state)

    def test_mailing_list_subscribe_existing(self):
        task = self.new_task(self.users[0])
        action = mailing_list.MailingListSubscribeAction(
            self.data, task=task, order=1)

        action.prepare()
        with mock.patch.object(
                mailing_list.Mailman,
                '_execute',
                return_value=[self.users[0].name]
        ) as mailman:
            action.approve()
            mailman.assert_called_once_with(
                '/usr/lib/mailman/bin/list_members kaizen-users'
            )
            self.assertEqual('complete', action.action.state)

        self.assertEqual('complete', action.action.state)

    def test_mailing_list_error_not_blocking(self):
        task = self.new_task(self.users[0])
        action = mailing_list.MailingListSubscribeAction(
            self.data, task=task, order=1)

        action.prepare()
        with mock.patch.object(
                mailing_list.Mailman,
                '__enter__',
                side_effect=paramiko.ssh_exception.SSHException()):
            action.approve()
            self.assertEqual('complete', action.action.state)

        self.assertEqual('complete', action.action.state)
