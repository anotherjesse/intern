INTERN
======

Finally someone to do your work for you...

A tool that wraps openstack apis and give some nice CLI tools

This is very **ALPHA**.  Everything is subject to change and is probably broken!!!

Usage
-----

Install:

 * git clone -b redux http://github.com/anotherjesse/intern.git
 * sudo python setup.py develop
 * intern

Configure:

 * edit ~/.intern/intern.conf
 * set user and admin creds - if you have them

Go:

 * list user servers: ``intern list``
 * delete 3 servers matching go-? pattern: ``intern delete go-? 3``
 * viz a cloud: ``intern watch | gource --realtime --log-format custom -i 3600 -``



