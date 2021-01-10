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


class Mailman(object):

    def __init__(self, hostname, port, username, key):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.key = key
        self.client = paramiko.client.SSHClient()


    def __enter__(self):
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            pkey=paramiko.RSAKey.from_private_key_file(self.key))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def _execute(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)

        errors = stderr.read()
        if errors:
            raise ConnectionError(errors)

        # Note(knikolla): Not entirely sure if closing before reading is fine.
        r = stdout.read().decode('utf-8').split('\n')
        return r

    def is_already_subscribed(self, email, list):
        command = ('/usr/lib/mailman/bin/list_members %s' % list)
        return email in self._execute(command)

    def subscribe(self, email, list):
        command = (
                'echo %s | /usr/lib/mailman/bin/add_members -r - %s'
                % (email, list)
        )
        self._execute(command)


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

    def _approve(self):
        try:
            with Mailman(self.config.host, self.config.port,
                         self.config.user, self.config.private_key) as mailman:
                if mailman.is_already_subscribed(self._get_email(),
                                                 self.config.list):
                    self.add_note('%s already subscribed to mailing list.'
                                  % self._get_email())
                else:
                    mailman.subscribe(self._get_email(), self.config.list)
                    self.add_note('%s successfully subscribed to mailing list.'
                                  % self._get_email())
        except paramiko.ssh_exception.SSHException as e:
            self.add_note('Unable to connect to Mailing List server. '
                          'Proceeding regardless. %s' % str(e))

        self.action.state = 'complete'
        self.action.save()

    def _submit(self, token_data):
        pass
