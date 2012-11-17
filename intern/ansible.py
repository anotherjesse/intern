import json
import sys

import intern.cloud
import intern.cluster


class Ansible(object):

    def __init__(self, name, image=None, flavor=None, spec=None):
        self.name = name
        self.spec = spec
        self.image = image
        self.flavor = flavor
        self.cluster = intern.cluster.Cluster(name)

    def list_json(self, build=True):
        if build:
            if self.cluster.build(self.spec):
                self.cluster.wait_for_ssh()

        groups = {}
        for vm in self.cluster:
            for g in vm['groups'].split(','):
                if g not in groups:
                    groups[g] = []
                groups[g].append(vm.ip)
        return json.dumps(groups)

    def host_json(self, ip):
        for vm in self.cluster:
            if vm.ip == ip:
                info = {
                    'os:uuid': vm.id,
                    'os:ip': vm.ip,
                    'os:name': vm.name
                }
                for k, v in vm.server.metadata.iteritems():
                    info['os:meta:%s' % k] = v
                return json.dumps(info)

    def cli(self):
        if len(sys.argv) < 2:
            print 'usage: ansible-playbook -i %s (playbook)' % sys.argv[0]
            sys.exit(1)

        cmd = sys.argv[1]
        if cmd == '--list':
            print self.list_json()
        elif cmd == '--host':
            ip = sys.argv[2]
            print self.host_json(ip)

