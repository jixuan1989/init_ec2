# -*- coding: utf-8 -*-
import fabfile
from fabric.api import *

env=fabfile.env

def __test():
    print fabfile.cf.get('server','hosts')

# currently, couchdb is not a cluster. instead, each node is a single instance. so you'd better to just use one node.
#just for ubuntu 14.04, see https://launchpad.net/~couchdb/+archive/ubuntu/stable

@roles('server')
def installCouch(multi='n'):
    if (len(env.hsots) > 1 and multi != 'y'):
        print "if you are sure that you want to install couchdb server on multi servers, please use `fab installCouch:y`"
        return
    else:
        if ((not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts):
            fabfile.__rootUser()
            sudo('apt-get install software-properties-common -y')
            sudo('add-apt-repository ppa:couchdb/stable -y')
            sudo('apt-get update -y')
            sudo('apt-get remove couchdb couchdb-bin couchdb-common -yf')
            sudo('apt-get install -V couchdb -y')
            sudo('couchdb stop')
            #TODO: mudify the listen address of couchdb.
            #sudo('')

@roles('server')
def installCollectd():
    if ((not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts):
        fabfile.__rootUser()
        sudo('apt-get install collectd -y')
        sudo("sed -i 's/#LoadPlugin network/LoadPlugin network/g' /etc/collectd/collectd.conf")
        configuration='<Plugin "network">\n\tServer "'+fabfile.cf.get('collectd','server_ip')+'" "'+fabfile.cf.get('collectd','server_port')+'"'+'\n</ Plugin >'
        sudo("echo '"+configuration+"' >>/etc/collectd/collectd.conf ")
        configuration=fabfile.cf.get('collectd','interval')
        sudo("sed -i 's/#Interval 10/Interval "+configuration+"/g' /etc/collectd/collectd.conf")
        sudo("/etc/init.d/collectd stop")
        sudo("/etc/init.d/collectd start")

@roles('server')
def runCollectd(status='start'):
    if ((not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts):
        fabfile.__rootUser()
        sudo("/etc/init.d/collectd "+status)


@roles('server')
def distributeCassandra():
    if ((not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts):
        __normalUser()
        print 'will create a temp file /home/username/fabric-cassandra.tar.gz'
        put(os.path.join(os.path.split(env.real_fabfile)[0], cf.get(activeSession,'jdk_source_file')), os.path.join('/home',env.user,'fabric-cassandra.tar.gz'))
        run('tar -xzf '+ os.path.join('/home',env.user,'fabric-cassandra.tar.gz'))
        run('echo "export JAVA_HOME='+os.path.join('/home/',env.user, cf.get(activeSession,'jdk_folder'))+'">>~/.bashrc')
        run("echo 'export PATH=$JAVA_HOME/bin:$PATH' >>~/.bashrc")
        run('rm '+os.path.join('/home',env.user,'fabric-jdk.tar.gz'))