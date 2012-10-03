import base64

class Script(object):

    def __init__(self):
        self.tasks = []

    def run(self, cmd):
        self.tasks.append(cmd)

    def put(self, dest, content, mode=None):
        encoded = base64.encodestring(content)
        cmd = "cat <<EOF | base64 -d > %s\n%sEOF" % (dest, encoded)
        if mode:
            cmd += "\nchmod %s %s" % (mode, dest)
        self.tasks.append(cmd)

    def upload(self, dest, src, mode=None):
        content = open(src, 'r').read()
        self.put(dest, content, mode)

    def bundle(self):
        return "#!/bin/sh\n\n%s" % ("\n\n".join(self.tasks))

