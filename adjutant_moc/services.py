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
import requests

from adjutant import exceptions as adjutant_exceptions


class Service(object):
    def __init__(self, url):
        self.url = url.rstrip("/")
        self.session = requests.session()

    def check_response(self, response: requests.Response):
        if response.status_code == 400:
            raise adjutant_exceptions.BaseAPIException(str(response.json()))

    def create_project(self, project_id, project_name):
        url = "%s/projects/%s" % (self.url, project_id)
        payload = {'displayName': project_name}
        r = self.session.put(url, data=json.dumps(payload))
        self.check_response(r)
        return r

    def get_project(self, project_id):
        url = "%s/projects/%s" % (self.url, project_id)
        r = self.session.get(url)
        self.check_response(r)
        return r

    def delete_project(self, project_id):
        url = "%s/projects/%s" % (self.url, project_id)
        r = self.session.delete(url)
        self.check_response(r)
        return r

    def create_user(self, username):
        url = "%s/users/%s" % (self.url, username)
        r = self.session.put(url)
        self.check_response(r)
        return r

    def get_user(self, username):
        url = "%s/users/%s" % (self.url, username)
        r = self.session.get(url)
        self.check_response(r)
        return r

    def delete_user(self, username):
        url = "%s/projects/%s" % (self.url, username)
        r = self.session.delete(url)
        self.check_response(r)
        return r

    def add_role(self, username, project_id, role):
        # /users/<user_name>/projects/<project_name>/roles/<role>
        url = "%s/users/%s/projects/%s/roles/%s" % (self.url, username,
                                                    project_id, role)
        r = self.session.put(url)
        self.check_response(r)
        return r

    def get_role(self, username, project_id, role):
        url = "%s/users/%s/projects/%s/roles/%s" % (self.url, username,
                                                    project_id, role)
        r = self.session.get(url)
        self.check_response(r)
        return r

    def delete_role(self, username, project_id, role):
        url = "%s/users/%s/projects/%s/roles/%s" % (self.url, username,
                                                    project_id, role)
        r = self.session.delete(url)
        self.check_response(r)
        return r
