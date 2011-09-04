#!/usr/bin/env python

import settings
import novaclient.v1_1.client

nova = novaclient.v1_1.client.Client(settings.user, settings.password,
                                     settings.tenant, settings.url)

from flask import Flask, request, render_template

app = Flask(__name__)

firstboot = "* * * * * root /bin/bash /root/job.sh\n"

@app.route("/")
def hello():
    return render_template('hello.html')

@app.route("/jobs", methods=['GET', 'POST'])
def jobs():
    if request.method == 'POST':
        userdata = request.form['src'].replace("\r", "")
        nova.servers.create(name="intern %s" % request.form['name'],
                            image=settings.image,
                            userdata=userdata,
                            #files={'/etc/cron.d/firstboot': firstboot,
                            #       '/root/job.sh': request.form['src']},
                            flavor=settings.flavor)
        return "new job %s" % request.form['name']
    else:
        servers = nova.servers.list()
        return render_template('jobs.html', servers=servers)

if __name__ == "__main__":
    app.run(debug=True)
