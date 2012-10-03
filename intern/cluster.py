class Cluster(object):
    """a collection of VMs"""

    def __init__(self, vms=None):
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

