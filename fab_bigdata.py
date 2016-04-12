# -*- coding: utf-8 -*-
import fabfile
from fabric.api import *
import os

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
            sudo('couchdb start')

@roles('server')
def runCouch(status='start',multi='n'):
    if (len(env.hsots) > 1 and multi != 'y'):
        print "if you are sure that you want to install couchdb server on multi servers, please use `fab installCouch:y`"
        return
    else:
        if ((not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts):
            fabfile.__rootUser()
            sudo('couchdb '+status)

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

#only client. you need to install server yourself now. (server has too many configurations that need to set. e.g., apache2 or nginx)
@roles('server')
def installGangliaClient():
    if ((not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts):
        fabfile.__rootUser()
        sudo('apt-get install -y ganglia-monitor')
        put(os.path.join(os.path.split(env.real_fabfile)[0], 'files/gmond.conf'),
            os.path.join('/home', env.user, 'fabric-gmond.conf'))
        sudo('cat '+os.path.join('/home', env.user, 'fabric-gmond.conf') +' > /etc/ganglia/gmond.conf')
        sudo('service ganglia-monitor restart')

@roles('server')
def distributeCassandra():
    if ((not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts):
        fabfile.__normalUser()
        print 'will create a temp file /home/username/fabric-cassandra.tar.gz'
        cf=fabfile.cf

        put(os.path.join(os.path.split(env.real_fabfile)[0], cf.get('cassandra','cassandra_file')), os.path.join('/home',env.user,'fabric-cassandra.tar.gz'))
        run('tar -xzf '+ os.path.join('/home',env.user,'fabric-cassandra.tar.gz'))
        cassandra_path=os.path.join('/home',env.user,cf.get('cassandra','cassandra_folder'))
        yaml=os.path.join(os.path.split(env.real_fabfile)[0], 'files/cassandra.yaml')
        logback=os.path.join(os.path.split(env.real_fabfile)[0], 'files/cassandra-logback.xml')
        put(yaml,os.path.join(cassandra_path,'conf/cassandra.yaml'))
        put(logback, os.path.join(cassandra_path, 'conf/logback.yaml'))

@roles('server')
def modifyCassandra():
    if ((not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts):
        fabfile.__normalUser()
        cassandra_path = os.path.join('/home', env.user, fabfile.cf.get('cassandra', 'cassandra_folder'))
        yaml = os.path.join(os.path.split(env.real_fabfile)[0], 'files/cassandra.yaml')
        put(yaml, os.path.join(cassandra_path, 'conf/cassandra.yaml'))

@roles('server')
def runCassandra(status='stop'):
    if ((not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts):
        fabfile.__normalUser()
        cassandra_path=os.path.join('/home',env.user,fabfile.cf.get('cassandra','cassandra_folder'))
        print cassandra_path
        if(status=='start'):
            run(os.path.join(cassandra_path,'bin/cassandra')+' -f -p cassandraPID')
        elif(status=='stop'):
            pid=run('cat '+os.path.join('/home',env.user,'cassandraPID'))
            run("kill "+pid)
        else:
            print 'unknow command '+ status+", only support start or stop"

@roles('server')
def rmCassandraData(status='stop'):
    if ((not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts):
        fabfile.__normalUser()
        run('rm -rf '+fabfile.cf.get('cassandra','data_folder'))
