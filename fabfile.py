# -*- coding: utf-8 -*-
from fabric.api import *
from fabric.contrib.console import confirm
import ConfigParser


cf=ConfigParser.ConfigParser()
cf.read('passwd.ini')
#env.hosts=['localhost']
env.disable_known_hosts=True
#env.key_filename=['~/Desktop/hxd.pem']
env.user=cf.get('global','root')
env.password = cf.get('global','passwd')
env.roledefs = {
    'server': {
        'hosts': ['192.168.130.3', '192.168.130.5', '192.168.130.6', '192.168.130.7', '192.168.130.8',
        '192.168.130.9', '192.168.130.11', '192.168.130.12', '192.168.130.13', '192.168.130.15',
        '192.168.130.16', '192.168.130.17', '192.168.130.18', '192.168.130.19', '192.168.130.20'],
    'ips': [ 's3', 's5', 's6', 's7', 's8',
       's9', 's11', 's12', 's13', 's15',
       's16', 's17', 's18', 's19', 's20']
    },
    'client': {
        'hosts': ['192.168.130.2'],
        'ips': ['s2']
    }
}
@roles('client')
def createClientUser():
    createUser(cf.get('client','newuser'),cf.get('client','passwd'))

@roles('server')
def createServerUser():
    createUser(cf.get('server','newuser'),cf.get('server','passwd'))

def createUser(name, passwd):
    with settings(warn_only=True):
        with settings(prompts={
            '输入新的 UNIX 密码： ': passwd,
            'Enter new UNIX password: ': passwd,
            '重新输入新的 UNIX 密码： ': passwd,
            'Retype new UNIX password: ': passwd,
            '全名 []: ':'\n',
            'Full Name []: ': '\n',
            '房间号码 []: ':'\n',
            'Room Number []: ': '\n',
            '工作电话 []: ': '\n',
            'Work Phone []: ': '\n',
            '家庭电话 []: ': '\n',
            'Home Phone []: ': '\n',
            '其它 []: ': '\n',
            'Other []: ': '\n',
            '这些信息是否正确？ [Y/n] ': 'y',
            'Is the information correct? [Y/n] ': 'y',
            }):
            sudo('adduser '+name ,pty=False, combine_stderr=False)

@roles('client')
def test():
    with settings(warn_only=True):
        cd('/')
        run('ls ./')
        #result = local('./manage.py test my_app', capture=True)
        #if result.failed and not confirm("Tests failed. Continue anyway?"):
        #    abort("Aborting at user request.")

def generateHosts():
    hosts=''
    i=0
    size=len(env.roledefs['server']['hosts'])
    while i<size:
        hosts = hosts + '\n' + env.roledefs['server']['ips'][i] + '\t' + env.roledefs['server']['hosts'][i]
        i=i+1
    return hosts


@roles('server','client')
def changeHostname():
    sudo('echo \'127.0.0.1 '+env.host+'\' >> /etc/hosts')
    sudo('echo '+ env.host+' >/etc/hostname' )
    sudo('hostname '+ env.host)
  #  print env.host
@roles('client')
def removeClientUser():
    sudo('deluser '+ cf.get('client','newuser'), pty=False, combine_stderr=False)