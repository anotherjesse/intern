from intern import cloud


class Cluster(object):
    """a collection of VMs"""

    def __init__(self, name=None):
        self.name = name
        self.refresh()

    def __setitem__(self, k, v):
        self.vms[k] = v

    def add(self, vm):
        self[vm.name] = vm

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
        self.vms = {}
        for vm in cloud.find():
            if vm['intern:cluster'] == self.name:
                self.add(vm)

    def build(self, spec):
        """ensure a cluster meets a given spec

        spec is a dictionary with keys of group(s) and value of qty

        returns true if any VM launched or terminated"""

        changed = False
        self.refresh()
        existing_names = [e.name for e in self]

        goal = {}
        for groups, qty in spec.iteritems():
            for n in xrange(qty):
                vm_name = '%s-%s-%d' % (self.name, groups, n)
                goal[vm_name] = {'groups': groups}

        for vm_name, meta in goal.iteritems():
            if vm_name not in existing_names:
                meta = {
                    'groups': meta['groups'],
                    'intern:cluster': self.name
                }
                flavor = {'ram': '2G'}
                vm = cloud.boot(vm_name, apt_proxy=True, meta=meta,
                                flavor=flavor, ping=False, enable_root=True)
                self.add(vm)
                changed = True

        for vm in self:
            if vm.name not in goal.keys():
                print 'deleting %s' % vm
                vm.delete()
                del self[vm.name]
                changed = True

        return changed


if __name__ == '__main__':
    c = Cluster('staging')
    if c.build({'apps': 2,
                'search,redis': 1,
                'db': 1,
                'cache': 1}):
        c.wait_for_ssh()
