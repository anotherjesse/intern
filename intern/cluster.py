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

    def refresh(self):
        """update the list of VMs for the current cluster"""
        self.vms = [v for v in cloud.find() if v['intern:cluster'] == self.name]

    def build(self, spec):
        """ensure a cluster meets a given spec

        spec is a dictionary with keys of group(s) and value of qty"""

        self.refresh()
        existing_names = [e.name for e in self.vms]

        goal = {}
        for groups, qty in spec.iteritems():
            for n in xrange(qty):
                vm_name = '%s-%s-%d' % (self.name, groups, n)
                goal[vm_name] = {'groups': groups}

        new_vms = []
        for vm_name, meta in goal.iteritems():
            if vm_name not in existing_names:
                meta = {'groups': meta['groups'], 'intern:cluster': self.name}
                flavor = {'ram': '2G'}
                vm = cloud.boot(vm_name, apt_proxy=True, meta=meta,
                                flavor=flavor, ping=False)
                new_vms.append(vm)

        for vm in self.vms:
            if vm.name not in goal.keys():
                print 'deleting %s' % vm
                vm.delete()


if __name__ == '__main__':
    c = Cluster('staging')
    c.build({'apps': 1,
             'search,redis': 1,
             'db': 1,
             'cache': 1})
