import os.path
import re
import subprocess
import time

from novaclient.v1_1 import client
from intern import cloudinit
from intern import utils
from intern import vm


##########
# Helpers
##########


user_conn = None
admin_conn = None
def nova(admin=False):
    CONF = utils.load_config("global")
    if admin:
        global admin_conn
        if not admin_conn:
            CREDS = utils.load_config("admin")
            admin_conn = client.Client(CREDS.get('user'),
                                      CREDS.get('password'),
                                      CREDS.get('tenant'),
                                      CONF.get('auth_endpoint'))
        return admin_conn
    else:
        global user_conn
        if not user_conn:
            CREDS = utils.load_config("user")
            user_conn = client.Client(CREDS.get('user'),
                                      CREDS.get('password'),
                                      CREDS.get('tenant'),
                                      CONF.get('auth_endpoint'))
        return user_conn


def ping(ip):
    try:
        subprocess.check_output(['ping', '-c1', '-w1', ip])
        return True
    except:
        pass


def wait_for_ping(ip):
    while not ping(ip):
        time.sleep(1)



##############
# cloud logic
##############


def find(pattern=None):
    """Find all server, optionally matching a pattern

    The server name must match the pattern

    pattern: j   server: 'applejacks'   -> NO
    pattern: j-? server: 'j-1'          -> YES
    """
    servers = [vm.VM(s) for s in nova().servers.list()]
    if pattern:
        p = re.compile('^%s$' % pattern)
        servers = [s for s in servers if p.match(s.name)]
    return servers


def find_image(name):
    images = nova().images.list()
    matches = [i for i in images if name in i.name]
    if len(matches) != 1:
        print 'Unable to match image name "%s"' % name
        for i in images:
            print ' -> %s' % i.name
        raise Exception('image')
    return matches[0]


def find_flavor(properties=None):
    if not properties:
        properties={}

    ram = utils.parse(properties.get('ram'))
    root = utils.parse(properties.get('root'), False)
    ephemeral = utils.parse(properties.get('ephemeral'), False)
    vcpus = utils.parse(properties.get('vcpus'), False)

    flavors = nova().flavors.list()
    if ram:
        flavors = [f for f in flavors if f.ram == ram]
    if root:
        flavors = [f for f in flavors if f.disk == root]
    if ephemeral:
        flavors = [f for f in flavors if f.ephemeral == ephemeral]
    if vcpus:
        flavors = [f for f in flavors if f.vcpus == vcpus]
    if len(flavors) > 1:
        print 'multiple flavors match...'
        for f in flavors:
            print ' -> %s' % f.ram
        raise Exception('flavor')
    if len(flavors) == 0:
        print 'Unable to find flavor matching %s' % properties
        if ram and vcpus and (root or ephemeral):
            # FIXME: flavorid needs to be uniq but provided by user :(
            flavorid = 0
            name = "intern-%sG-%s-%s/%s" % ((ram/1024), vcpus, root, ephemeral)
            print 'creating %s' % name
            f = nova(admin=True).flavors.create(name,
                                                ram=ram,
                                                vcpus=vcpus,
                                                disk=root,
                                                flavorid=flavorid,
                                                ephemeral=ephemeral)
            return f
        else:
            print 'not enough parameters to create, current options'
            for f in nova().flavors.list():
                print ' -> %s' % f.ram
            raise Exception('flavor')
    return flavors[0]


def delete(name, qty=1):
    """delete servers that match regexp name

    as a safegaurd, you must specify many servers you expect to delete"""
    servers = find(name)
    if len(servers) != qty:
        found = len(servers)
        print "ERROR: expected %d found %d named '%s'" % (qty, found, name)
        raise Exception('delete')
    for s in servers:
        print "deleting: %s" % s
        nova().servers.delete(s)


def boot(name, image='quantal', flavor=None, script=None, ping=True,
         packages=None, apt_proxy=None, floating_ip=None):
    """boot a VM with properties:

      * name: name of the VM
      * image: name of image to use
      * flavor: dict of flavor properties - create a flavor if none exists
      * apt_proxy: configure cloud-init enabled VMs for an apt_proxy
      *            pass either the http string or True to use global config
      * packages: list of apt packages to install
      * script: shell script to run on boot
      * ping: return from boot command only after ping to VM succeeds
      * floating_ip: True: grab an unassociated IP or allocate an IP
      *              or if a specific IP is passed, use it
    * """
    # FIXME: add image if not present
    image = find_image(image)
    print ' -> Image: %s' % image.name
    flavor = find_flavor(flavor)
    print ' -> VM: %s' % flavor.name

    try:
        key_path = os.path.expanduser('~/.ssh/id_rsa.pub')
        key = open(key_path).read()
    except:
        key = None

    # IDEA: in addition to passing True or http://example, pass the name
    # of a host and we convert it to an ip?
    if apt_proxy is True:
         CONF = utils.load_config("global")
         apt_proxy = CONF.get('apt_proxy')

    if floating_ip is True:
        # Find an unused IP or get one...
        # FIXME - allow a user to send an IP
        ips = nova().floating_ips.list()
        unused = [i for i in ips if i.instance_id is None]
        if len(unused) == 0:
            fip = nova().floating_ips.create()
        else:
            fip = unused[0]
        print " -> floating ip: %s" % fip.ip

    userdata = cloudinit.cloudconfig({'apt_proxy': apt_proxy,
                                      'ssh_key': key,
                                      'hostname': name,
                                      'packages': packages,
                                      'script': script})
    #meta = {
    #    'dsmode': 'local',
    #}

    s = nova().servers.create(name,
                         image.id,
                         flavor.id,
                         #meta=meta,
                         #nic='net-id=82559d25-78e9-44f5-a1e2-3e8f735056c0',
                         userdata=userdata)
                         #config_drive=True)

    print "building: %s" % s.id

    print 'waiting for ip...'

    ip4 = None
    while ip4 is None:
        time.sleep(1)
        s = nova().servers.get(s)
        if s.state == 'ERROR':
            raise Exception('errored')
        ip4 = utils.extract_ip4(s.networks)

    print 'IP: %s' % ip4

    if floating_ip is True:
        s.add_floating_ip(fip)

    if ping:
        print 'waiting for network (ping) ...'
        wait_for_ping(ip4)

    print 'success'
    return vm.VM(s)
