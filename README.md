intern
======

ask it to do stuff for you

upon asking (uploading a script to pastebin), intern will:

 * spins up a vm
 * execute the script on the vm
 * reports back the status

Useful for when you have better things to do ...  (and you want to use cpu or
bandwidth in the cloud)

examples:

 * download / upload an image to glance
 * rebuild debian packages
 * using debootstrap to build new images

Getting started
---------------

    pip install Flask
    pip install python-novaclient
    # create a settings.py
    python serve.py


TODO
----

 * how to upload script? currently uses userdata as:
   * injected files don't work: https://bugs.launchpad.net/nova/+bug/755168
 * simple cli: intern (script_name) [args]
 * how to report result
 * how to terminate instances when complete
 * user accounts

Ideas
-----

 * allow creation of library of parameterized scripts (ala yubnub)
 * easy to use cli / library api
 * results returned via dropbox (so you get a growl)
 * launch new vm via dropping a file in dropbox
 * scripts in other langauges like python/ruby
 * scripts as chef recipes
 * specify environment via chef/puppet recipes?
 * pickle your env and upload it?
 * use lxc containers instead of kvm/xen?
 * tail result file if uploaded
 * upload results as multi-chunk file to swift
 * allow jobs easy access to swift bucket?
