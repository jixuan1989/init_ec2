# -*- coding: utf-8 -*-
from fabric.api import *
from fabric.contrib.console import confirm
import ConfigParser


cf=ConfigParser.ConfigParser()
cf.read('passwd.ini')
activeSession=cf.get('global','activeSession')
#env.hosts=['localhost']
env.disable_known_hosts=True
#env.key_filename=['~/Desktop/hxd.pem']
env.user=cf.get('global','root')
env.password = cf.get('global','passwd')

def lambdastrp(x):
    return x.strip()

class MyEnv:
    hosts=[]
    hostnames=[]
    hostmap={}
myenv=MyEnv()
myenv.hosts=map(lambdastrp, cf.get(activeSession,'hosts').split(','))
myenv.hostnames=map(lambdastrp,cf.get(activeSession,'hostnames').split(','))

i=0
while i<len(myenv.hosts):
    myenv.hostmap[myenv.hosts[i]]=myenv.hostnames[i]
    i=i+1

env.roledefs={
    'root':{
        'hosts':myenv.hosts
    },
    'server':{
        'hosts':myenv.hosts
    }

}
#env.roledefs = {
#    'server': {
#        'hosts': ['192.168.130.3', '192.168.130.5', '192.168.130.6', '192.168.130.7', '192.168.130.8',
#        '192.168.130.9', '192.168.130.11', '192.168.130.12', '192.168.130.13', '192.168.130.15',
#        '192.168.130.16', '192.168.130.17', '192.168.130.18', '192.168.130.19', '192.168.130.20'],
#    'ips': [ 's3', 's5', 's6', 's7', 's8',
#       's9', 's11', 's12', 's13', 's15',
#       's16', 's17', 's18', 's19', 's20']
#    },
#    'client': {
#        'hosts': ['192.168.130.2'],
#        'ips': ['s2']
#    },
#    'test':{
#        'hosts': ['localhost']
#    }
#}
user=cf.get(activeSession,'newuser')
passwd=cf.get(activeSession,'passwd')
#批量创建用户
@roles('root')
def createUser():
    with settings(warn_only=True):
        with settings(prompts={
            '输入新的 UNIX 密码： ': passwd,
            'Enter new UNIX password: ': passwd,
            '重新输入新的 UNIX 密码： ': passwd,
            'Retype new UNIX password: ': passwd,
            '全名 []: ':'hxd',
            'Full Name []: ': 'hxd',
            '房间号码 []: ':'no',
            'Room Number []: ': 'no',
            '工作电话 []: ': '130',
            'Work Phone []: ': '130',
            '家庭电话 []: ': '130',
            'Home Phone []: ': '130',
            '其它 []: ': 'no',
            'Other []: ': 'no',
            '这些信息是否正确？ [Y/n] ': 'Y',
            'Is the information correct? [Y/n] ': 'Y',
            }):
            sudo('adduser '+user ,pty=True, combine_stderr=True)
#批量删除用户
@roles('root')
def removeUser():
    sudo('deluser '+ user, pty=True, combine_stderr=True)

#修改hosts
@roles('root')
def addIntoHostFile():
    sudo('echo "' + generateHosts() + '" >> /etc/hosts')

def generateHosts():
    hosts=''
    i=0
    size=len(myenv.hosts)
    while i<size:
        hosts = hosts + '\n' + myenv.hosts[i] + '\t' + myenv.hostnames[i]
        i=i+1

    return hosts

#修改hostname
@roles('root')
def changeHostname():
    hostname=myenv.hostmap[env.host]
#    print hostname
    sudo('echo \'127.0.0.1 '+hostname+'\' >> /etc/hosts')
    sudo('echo '+ hostname+' >/etc/hostname' )
    sudo('hostname '+ hostname)

def downloadJDK():
    pass
#    local('wget --no-check-certificate --no-cookies --header Cookie: oraclelicense=accept-securebackup-cookie http://download.oracle.com/otn-pub/java/jdk/8u73-b02/jdk-8u73-linux-x64.tar.gz')
@roles('root')
def distributeJDK():
    #with lcd("~"):
	#put('/home/hxd/jdk1.8.77.tar.gz', './jdk1.8.77.tar.gz')
    	#run('tar -xzf jdk1.8.77.tar.gz')
    	run('echo "export JAVA_HOME=/home/'+env.user+'/jdk1.8.0_77">>~/.bashrc')
    	run("echo 'export PATH=$JAVA_HOME/bin:$PATH' >>~/.bashrc")

@roles('server')
def test3():
    env.user=cf.get('client','newuser')
    env.password=cf.get('client','passwd')
    test2()

def test2():
        run('ls ./')

@roles('test')
def test():
    with settings(warn_only=True):
        cd('/')
        run('ls ./')
        #result = local('./manage.py test my_app', capture=True)
        #if result.failed and not confirm("Tests failed. Continue anyway?"):
        #    abort("Aborting at user request.")

def test4():
    a=cf.get('client','hosts')
    a=a.split(',')
    print type(a)
    print a

@roles('server')
def test5():
    print env.real_fabfile
    run('ls ./')