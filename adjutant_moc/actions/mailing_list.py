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

from confspirator import groups as conf_group
from confspirator import fields as conf_field
import paramiko

from adjutant.config import CONF

from adjutant_moc.actions import serializers
from adjutant_moc.actions import base


# TODO knikolla: there are going to be issues here when we
# add invited users, since get email returns the one who created the task.
class MailingListSubscribeAction(base.MocBaseAction):

    required = [
        'email'
    ]

    serializer = serializers.MailingListSubscribeSerializer

    config_group = conf_group.DynamicNameConfigGroup(
        children=[
            conf_field.StrConfig(
                "private_key",
                help_text="Location of private key for mailing list server.",
                default="/.ssh/id_rsa",
                sample_default="/.ssh/id_rsa",
            ),
            conf_field.HostNameConfig(
                "host",
                help_text="Mailing list server host.",
                default="mail.massopen.cloud",
                sample_default="mail.massopen.cloud",
            ),
            conf_field.IntConfig(
                "port",
                help_text="Mailing list server SSH port",
                default=22,
                sample_default=22,
            ),
            conf_field.StrConfig(
                "user",
                help_text="Mailing list server user.",
                default="moc-tools",
                sample_default="moc-tools",
            ),
            conf_field.StrConfig(
                "list",
                help_text="Mailing list to add users to.",
                default="kaizen-users",
                sample_default="kaizen-users",
            ),
        ],
    )

    def _get_email(self):
        if CONF.identity.username_is_email:
            return self.action.task.keystone_user['username']

    def _mailman(self, command):
        key = paramiko.RSAKey.from_private_key_file(
            self.config.private_key)
        client = paramiko.client.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=self.config.host,
                       port=self.config.port,
                       username=self.config.user,
                       pkey=key)

        stdin, stdout, stderr = client.exec_command(command)

        errors = stderr.read()
        if errors:
            self.add_note('Error executing mailman command, check logs.')
            raise ConnectionError(errors)

        # Note(knikolla): Not entirely sure if closing before reading is fine.
        r = stdout.read().decode('utf-8').split('\n')
        client.close()
        return r

    def _is_already_subscribed(self):
        command = ('/usr/lib/mailman/bin/list_members %s'
                   % self.config.list)
        members = self._mailman(command)
        return self._get_email() in members

    def _subscribe(self):
        command = (
                'echo %s | /usr/lib/mailman/bin/add_members -r - %s'
                % (self._get_email(), self.config.list)
        )
        self._mailman(command)

    def _approve(self):
        if self._is_already_subscribed():
            self.add_note('Email %s already subscribed to mailing list.'
                          % self._get_email())
        else:
            self._subscribe()
            self.add_note('Email %s successfully subscribed to mailing list.'
                          % self._get_email())
        self.action.state = 'complete'
        self.action.save()

    def _submit(self, token_data):
        pass
