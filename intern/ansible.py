import json
import sys

import intern.cloud
import intern.cluster


def cluster(name):
    return intern.cluster.Cluster(name)


def list_json(cluster, spec, build=True):
    if build:
        if cluster.build(spec):
            cluster.wait_for_ssh()
    groups = {}
    for vm in cluster:
        for g in vm['groups'].split(','):
            if g not in groups:
                groups[g] = []
            groups[g].append(vm.ip)
    return json.dumps(groups)


def host_json(cluster, ip):
    for vm in cluster:
        if vm.ip == ip:
            info = {
                'os:uuid': vm.id,
                'os:ip': vm.ip,
                'os:name': vm.name
            }
            for k, v in vm.server.metadata.iteritems():
                info['os:%s' % k] = v
            return json.dumps(info)


def go(name, image, flavor, spec):
    if len(sys.argv) < 2:
        print 'usage: ansible-playbook -i %s (playbook)' % sys.argv[0]
        sys.exit(1)

    cmd = sys.argv[1]
    cluster = intern.cluster.Cluster(name)
    if cmd == '--list':
        print list_json(cluster, spec)
    elif cmd == '--host':
        ip = sys.argv[2]
        print host_json(cluster, ip)

