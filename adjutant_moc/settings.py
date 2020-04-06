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

import sys


import confspirator
from confspirator import groups as config_groups
from confspirator import fields as config_fields
import yaml


TESTING = sys.argv[1:2] == ['test']

moc = config_groups.ConfigGroup("moc")
services = config_fields.DictConfig(
    'services',
    default={'openshift': {'type': 'openshift',
                           'url': 'https://example.com'}})
moc.register_child_config(services)

conf_dict = None
try:
    with open('/etc/adjutant/services.yaml', 'r') as f:
        conf_dict = yaml.load(f, Loader=yaml.FullLoader)
except FileNotFoundError:
    pass

MOC_CONF = confspirator.load(moc, {'moc': conf_dict})
