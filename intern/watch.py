# Copyright 2012 Dean Troyer
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Return some stats from the OpenStack Nova API in gource format
"""

import time
import sys

from intern import cloud
from keystoneclient.v2_0 import client as keystone_client

search_opts = {'all_tenants': 1}
show_host = True

admin_key = None
user_key = None
def keystone(admin=False):
    raise Exception('unimplemented')
    if admin is False:
        raise Exception('unimplemented')

    CREDS = utils.load_config("admin")
    conn = keystone_client.Client(token=user.token.id,
                                  endpoint=endpoint)

    keystone_client.keystone.user_list(self.request)


def tenant_name(tenant_id):
    # FIXME: implement me
    return tenant_id


def user_name(user_id):
    # FIXME: implement me
    return user_id


def update_vms(vms):
    old_vms = vms.keys()
    new_vms = []
    servers = cloud.nova(True).servers.list(search_opts=search_opts)
    # First add anything that exists now
    for s in servers:
        new_vms.append(s.id)
        if s.id not in old_vms:
            tenant = tenant_name(s.tenant_id)
            host = s._info['OS-EXT-SRV-ATTR:host']
            try:
                parts = host.split('-')
                host = '%s/%s' % (parts[1], parts[0])
            except:
                pass
            user = user_name(s.user_id)
            vms[s.id] = {
                'name': s.name,
                'kind': 'vm',
                'user': user,
                'host': host,
                'tenant': tenant
            }
            log("A", vms[s.id])

    # Remove anything that used to exist
    for id in old_vms:
        if id not in new_vms:
            log("D", vms[id])
            del vms[id]

def log(kind, obj):
    # http://code.google.com/p/gource/wiki/CustomLogFormat
    timestamp = int(time.time())
    # kind should be (A)dded, (M)odified or (D)eleted
    print "%d|%s|%s|%s/%s/%s" % (timestamp, obj['user'], kind, obj['host'], obj['tenant'], obj['name'])
    sys.stdout.flush()

