from intern import conn
from intern import utils

import paramiko


class VM(object):

    def __init__(self, server):
        self.server = server
        self.ssh = None

    @property
    def id(self):
        return self.server.id

    @property
    def ip(self):
        return utils.extract_ip4(self.server.networks)

    def delete(self):
        conn.nova().servers.delete(self.server.id)

    @property
    def ips(self):
        return ' '.join(sum(self.server.networks.values(), []))

    def update(self):
        self.server = conn.nova().servers.get(self.server)

    @property
    def floating_ip(self):
        # What the heck?  floating ips are the second private ip?
        if len(self.server.networks['private']) > 1:
            return self.server.networks['private'][1]

    @property
    def name(self):
        return self.server.name

    @property
    def status(self):
        # FIXME: should this refresh?
        return self.server.status

    def __str__(self):
        return '<VM "%s">' % self.server.name

    def connect(self, max_tries=1):
        if self.ssh:
            return True
        #print "attempting to connect to %s" % self.ip
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
                #print "unable to connect to %s" % self.ip
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
        """return a string that is the content of a remote file"""
        if self.connect():
            sftp = self.ssh.open_sftp()
            resp = sftp.open(path).read()
            sftp.close()
            return resp
        else:
            raise Exception('connect')

    def put(self, path, content, mode=None):
        """upload a text file to the remote server"""
        if self.connect():
            sftp = self.ssh.open_sftp()
            resp = sftp.open(path, 'w').write(content)
            if mode:
                sftp.chmod(path, mode)
            sftp.close()
            return resp
        else:
            raise Exception('connect')
