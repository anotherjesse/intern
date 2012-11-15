from intern import cloud


class Cluster(object):
    """a collection of VMs"""

    def __init__(self, name=None, vms=None):
        self.name = name
        if vms:
            self.vms = vms
        else:
            self.vms = {}

    def __setitem__(self, k, v):
        self.vms[k] = v

    def __len__(self):
        return len(self.vms)

    def __iter__(self):
        return self.vms.itervalues()

    def wait_for_ssh(self):
        for vm in self:
            vm.wait_for_ssh()

    def run(self, cmd):
        for vm in self:
            vm.run(cmd)

    def put(self, path, content, mode=None):
        for vm in self:
            vm.put(path, content, mode=None)

    def get(self, path):
        for vm in self:
            yield vm.get(path)

    def build(self, name, spec):
        """initialize a named cluster with a spec

        spec is a dictionary with keys of group(s) and value of qty"""
        self.name = name

        existing = [v for v in cloud.find() if v.server.metadata.get('cluster', None) == self.name]

        existing_names = [e.name for e in existing]

        goal = {}
        for groups, qty in spec.iteritems():
            for n in xrange(qty):
                vm_name = '%s-%s-%d' % (self.name, groups, n)
                goal[vm_name] = {'groups': groups}

        new_vms = []
        for vm_name, meta in goal.iteritems():
            if vm_name not in existing_names:
                meta = {'groups': meta['groups'], 'cluster': self.name}
                flavor = {'ram': '2G'}
                vm = cloud.boot(vm_name, apt_proxy=True, meta=meta,
                                flavor=flavor, ping=False)
                new_vms.append(vm)

        for vm in existing:
            if vm.name not in goal.keys():
                print 'deleting %s' % vm
                vm.delete()


if __name__ == '__main__':
    c = Cluster()
    c.build('staging', {'apps': 2,
                        'search,redis': 1,
                        'db': 1,
                        'cache': 1})
