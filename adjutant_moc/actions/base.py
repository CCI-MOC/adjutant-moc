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

from adjutant.actions.v1 import base
from adjutant.common import user_store


ACTION_STATE_APPROVE_COMPLETED = "approve_completed"
ACTION_STATE_SUBMIT_COMPLETED = "submit_completed"


class MocBaseAction(base.BaseAction, base.ProjectMixin, base.UserMixin):

    def __init__(self, *args, **kwargs):
        self.leader_identity = user_store.IdentityManager()

        self.approve_journal = []
        self.submit_journal = []

        self.parent_id = None

        super().__init__(*args, **kwargs)

    def _validate(self):
        """Cycles through all the required attributes and validates them."""
        all_valid = True
        for data in self.required:
            try:
                valid = self.__getattribute__('validate_%s' % data)()
                self.add_note('%s is %s' % (data, str(valid)))
                if not valid:
                    all_valid = False
            except AttributeError:
                # No validation needed for this attribute
                continue

        if not all_valid:
            self.action.valid = False
        else:
            self.add_note('All required data is valid.')
            self.action.valid = True
        self.action.save()
        return all_valid

    def _get_user(self):
        return self.action.task.keystone_user

    def _prepare(self):
        self._validate()

    @staticmethod
    def find_services_for_project(project):
        return [tag.replace('service:', '') for tag in project.list_tags()]

    def set_cache(self, key, value):
        # Not entirely sure why there are two caches. Let's just set both.
        super(MocBaseAction, self).set_cache(key, value)
        self.action.task.cache[key] = value

    def write_to_approve_journal(self):
        raise NotImplementedError

    def write_to_submit_journal(self, token_data):
        raise NotImplementedError

    def _approve(self):
        if self.action.state in [ACTION_STATE_APPROVE_COMPLETED,
                                 ACTION_STATE_SUBMIT_COMPLETED]:
            self.add_note('Action already completed approve or submit.')
            return True

        self._validate()

        if not self.valid:
            return

        self.write_to_approve_journal()

        self.add_note('Approve journal %s' % str([type(o) for o
                                                  in self.approve_journal]))

        # TODO: Make running the journal a separate function that
        # acce
        performed = []
        cache = {}
        try:
            for op in self.approve_journal:
                # Commit the operation, and update the cache
                # and logs
                op.commit(cache)
                for k, v in cache.items():
                    self.set_cache(k, v)
                self.add_note('executed: %s' % str(type(op)))
                for log in op.log:
                    self.add_note(log)
                performed.append(op)
        except Exception as e:
            self.add_note('Exception!: %s' % str(e))
            for op in reversed(performed):
                op.rollback(cache)
                for log in op.log:
                    self.add_note(log)
            raise e

        self.action.state = ACTION_STATE_APPROVE_COMPLETED
        self.action.save()

    def _submit(self, token_data):
        if self.action.state == ACTION_STATE_SUBMIT_COMPLETED:
            self.add_note("Action already completed submit.")
            return True
        self._validate()

        if not self.valid:
            return

        self.write_to_submit_journal(token_data)

        self.add_note('Submit journal %s' % str([type(o) for o
                                                 in self.approve_journal]))

        performed = []
        cache = {}
        try:
            for op in self.submit_journal:
                op.commit(cache)
                self.add_note('executed: %s' % str(type(op)))
                for k, v in cache.items():
                    self.set_cache(k, v)
                for log in op.log:
                    self.add_note(log)
                performed.append(op)
        except Exception as e:
            self.add_note('Exception!: %s' % str(e))
            for op in reversed(performed):
                op.rollback(cache)
                for log in op.log:
                    self.add_note(log)
            raise e

        self.action.state = ACTION_STATE_SUBMIT_COMPLETED
        self.action.save()

    def validate_token(self, token_data):
        pass
