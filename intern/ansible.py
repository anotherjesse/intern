import json
import sys

import intern.cloud
import intern.cluster


class Ansible(intern.cluster.Cluster):

    def __init__(self, name, image=None, flavor=None, spec=None, hostvars=None):
        self.spec = spec
        self.image = image
        self.flavor = flavor
        self.hostvars = hostvars
        super(Ansible, self).__init__(name)

    def list_json(self):

        groups = {}
        for vm in self:
            for g in vm['groups'].split(','):
                if g not in groups:
                    groups[g] = []
                groups[g].append(vm.ip)
        return json.dumps(groups, sort_keys=True, indent=2)

    def host_json(self, ip):
        for vm in self:
            if vm.ip == ip:
                info = {
                    'os:uuid': vm.id,
                    'os:ip': vm.ip,
                    'os:name': vm.name
                }
                if self.hostvars:
                    info.update(self.hostvars)
                for k, v in vm.server.metadata.iteritems():
                    info['os:meta:%s' % k] = v
                return json.dumps(info, sort_keys=True, indent=2)

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
        elif cmd == '--kill':
            # FIXME(ja): should probably wait until they disappear
            for vm in self:
                vm.delete()
        elif cmd == '--build':
            if self.build(self.spec):
                self.wait_for_ssh()
            print 'spec complete'

