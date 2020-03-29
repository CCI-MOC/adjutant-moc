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

from adjutant.api.v1 import base
from adjutant.common import user_store
from rest_framework.response import Response
from django.utils import timezone


class MocBaseApi(base.BaseDelegateAPI):

    task_type = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.identity = user_store.IdentityManager()

    @staticmethod
    def response_error(message, status):
        return Response({'errors': [message]}, status=status)

    def create_task(self, request):
        self.logger.info(
            "(%s) - Starting new project task." % timezone.now())

        self.task_manager.create_from_request(self.task_type, request)

        return Response({'notes': ['task created']}, status=202)
