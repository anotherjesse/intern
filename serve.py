#!/usr/bin/env python

import settings
import novaclient.v1_1.client

nova = novaclient.v1_1.client.Client(settings.user, settings.password,
                                     settings.tenant, settings.url)

from flask import Flask, request

app = Flask(__name__)

firstboot = "* * * * * root /bin/bash /root/job.sh\n"

@app.route("/")
def hello():
    return open('hello.html').read()

@app.route("/jobs", methods=['GET', 'POST'])
def jobs():
    if request.method == 'POST':
        nova.servers.create(name="intern %s" % request.form['name'],
                            image=settings.image,
                            files={'/etc/cron.d/firstboot': firstboot,
                                   '/root/job.sh': request.form['src']},
                            flavor=settings.flavor)
        return "new job %s" % request.form['name']
    else:
        servers = nova.servers.list()
        return "<ul>" + ''.join(["<li>%s" % s.name for s in servers])

if __name__ == "__main__":
    app.run(debug=True)
