import os.path
import subprocess
import sys
import time

import paramiko
from novaclient.v1_1 import client
from intern import utils


##########
# Helpers
##########

def extract_ip4(networks, kind=None):
    try:
        if kind:
            kinds = [kind]
        else:
            kinds = networks.keys()
        for kind in kinds:
            ips = [n for n in networks[kind] if len(n) < 16]
            if len(ips) > 0:
                return ips[0]
    except:
        pass


def ping(ip):
    try:
        subprocess.check_output(['ping', '-c1', '-w1', ip])
        return True
    except:
        pass


def wait_for_ping(ip):
    while not ping(ip):
        time.sleep(1)


class VM(object):

    def __init__(self, ip):
        self.ip = ip
        self.ssh = None

    def __str__(self):
        return '<VM "%s">' % self.ip

    def connect(self, max_tries=1):
        if self.ssh:
            return True
        key = paramiko.RSAKey.from_private_key_file('/home/jesse/.ssh/id_rsa')
        tries = 0
        while(True):
            try:
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.WarningPolicy())
                c.connect(self.ip, username='ubuntu', pkey=key, timeout=1)
                self.ssh = c
                return True
            except (paramiko.AuthenticationException, paramiko.SSHException):
                tries += 1
                if tries > max_tries:
                    raise

    def wait_for_ssh(self):
        while True:
            try:
                self.connect()
                self.run('uptime')
                return
            except:
                pass

    def run(self, cmd, max_tries=1):
        if self.connect(max_tries):
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            return stdout.read()

    def get(self, path):
        if self.connect():
            sftp = self.ssh.open_sftp()
            resp = sftp.open(path).read()
            sftp.close()
            return resp

    def put(self, path, content):
        if self.connect():
            sftp = self.ssh.open_sftp()
            resp = sftp.open(path, 'w').write(content)
            sftp.close()
            return resp


##############
# cloud logic
##############


def cloudconfig(options):
    lines = ['#cloud-config']
    if 'ssh_key' in options:
        lines.append('ssh_authorized_keys:\n - %s' % options['ssh_key'])
    if 'apt_proxy' in options:
        lines.append('apt_proxy: %s' % options['apt_proxy'])
    if 'hostname' in options:
        lines.append('hostname: %s' % options['hostname'])
    if options.get('script', None):
        lines.append('runcmd:\n - |')
        for l in options['script'].split('\n'):
            lines.append('  %s' % l)
    return '\n'.join(lines)


def find_image(name):
    images = nova().images.list()
    matches = [i for i in images if name in i.name]
    if len(matches) != 1:
        print 'Unable to match image name "%s"' % name
        for i in images:
            print ' -> %s' % i.name
        sys.exit(1)
    return matches[0]


def find_flavor(ram='2GB'):
    ram = ram.upper()
    if 'G' in ram:
        ram = 1024 * int(ram.split('G')[0])
    elif 'M' in ram:
        ram = int(ram.split('M')[0])
    else:
        ram = int(ram)
    flavors = nova().flavors.list()
    matches = [f for f in flavors if f.ram == ram]
    if len(matches) != 1:
        print 'Unable to find flavor with size "%s"' % ram
        for f in flavors:
            print ' -> %s' % f.ram
        sys.exit(1)
    return matches[0]

def delete(name, qty):
    servers = nova().servers.list()
    matches = [s for s in servers if s.name == name]
    if len(matches) != qty:
        found = len(matches)
        print "ERROR: expected %d found %d named '%s'" % (qty, found, name)
        sys.exit(1)
    for s in matches:
        print "deleting: %s" % s
        nova().servers.delete(s)

def nova(user=True):
    CONF = utils.load_config("global")
    if user:
        CREDS = utils.load_config("user")
    else:
        CREDS = utils.load_config("admin")

    return client.Client(CREDS.get('user'), CREDS.get('password'),
                         CREDS.get('tenant'), CONF.get('auth_endpoint'))


def list():
    return nova().servers.list()


def boot(name, image='quantal', ram='2GB', script=None, ping=True, user=True):
    # FIXME: add image if not present
    image = find_image(image)
    print ' -> Image: %s' % image.name
    flavor = find_flavor(ram)
    print ' -> VM: %s ram' % flavor.ram
    script = "#!/bin/sh\necho ubuntu:ubuntu | chpasswd"

    try:
        key_path = os.path.expanduser('~/.ssh/id_rsa.pub')
        key = open(key_path).read()
    except:
        key = None

    userdata = cloudconfig({'apt_proxy': 'http://10.0.0.1:3142',
                            'ssh_key': key,
                            'hostname': name,
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
        ip4 = extract_ip4(s.networks)

    print 'IP: %s' % ip4

    if ping:
        print 'waiting for network (ping) ...'
        wait_for_ping(ip4)

    print 'success'
    return VM(ip4)
