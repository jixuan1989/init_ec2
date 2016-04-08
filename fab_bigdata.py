# -*- coding: utf-8 -*-
import fabfile
from fabric.api import *

env=fabfile.env

def test():
    print fabfile.cf.get('server','hosts')

# currently, couchdb is not a cluster. instead, each node is a single instance. so you'd better to just use one node.
#just for ubuntu 14.04, see https://launchpad.net/~couchdb/+archive/ubuntu/stable

def installCouch():
    fabfile.__rootUser()
    sudo('apt-get install software-properties-common -y')
    sudo('add-apt-repository ppa:couchdb/stable -y')
    sudo('apt-get update -y')
    sudo('apt-get remove couchdb couchdb-bin couchdb-common -yf')
    sudo('apt-get install -V couchdb -y')
    sudo('couchdb stop')

@roles('server')
def installCollectd():
    fabfile.__rootUser()
    sudo('apt-get install collectd -y')
    sudo("sed -i 's/#LoadPlugin network/LoadPlugin network/g' /etc/collectd/collectd.conf")
    configuration='<Plugin "network">\n\tServer "'+fabfile.cf.get('collectd','inflexdb_ip')+'" "'+fabfile.cf.get('collectd','inflexdb_port')+'"'+'\n</ Plugin >'
    sudo("echo '"+configuration+"' >>/etc/collectd/collectd.conf ")

    sudo("/etc/init.d/collectd stop")
    sudo("/etc/init.d/collectd start")