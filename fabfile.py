# -*- coding: utf-8 -*-
from fabric.api import *
from fabric.contrib.console import confirm
import ConfigParser
import os
import fileinput


cf=ConfigParser.ConfigParser()
cf.read('passwd.ini')
activeSession=cf.get('default','activeSession')
#env.hosts=['localhost']
env.disable_known_hosts=True

# if you use Amazon Ec2. you need comment env.password=.... in __rootUser()  and use the below code
#env.key_filename=['~/Desktop/hxd.pem']

def __rootUser():
    env.user=cf.get('default','root')
    env.password=cf.get('default','passwd')
def __normalUser():
    env.user=cf.get(activeSession,'newuser')
    env.password = cf.get(activeSession,'passwd')
__normalUser()

def __lambdastrp(x):
    return x.strip()

class __MyEnv:
    hosts=[]
    hostnames=[]
    hostmap={}
myenv=__MyEnv()
myenv.hosts=map(__lambdastrp, cf.get(activeSession,'hosts').split(','))
myenv.hostnames=map(__lambdastrp,cf.get(activeSession,'hostnames').split(','))

i=0
while i<len(myenv.hosts):
    myenv.hostmap[myenv.hosts[i]]=myenv.hostnames[i]
    i=i+1

env.roledefs={
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


#批量创建用户
@roles('server')
def createUser():
    with settings(warn_only=True):
        passwd=cf.get(activeSession,'passwd')
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
            __rootUser()
            sudo('adduser '+cf.get(activeSession,'newuser') ,pty=True, combine_stderr=True)
#批量删除用户
@roles('server')
def removeUser():
    __rootUser()
    sudo('deluser '+ cf.get(activeSession,'newuser'), pty=True, combine_stderr=True)

#修改hosts
@roles('server')
def addIntoHostFile():
    __rootUser()
    sudo('echo "' + __generateHosts() + '" >> /etc/hosts')

def __generateHosts():
    hosts=''
    i=0
    size=len(myenv.hosts)
    while i<size:
        hosts = hosts + '\n' + myenv.hosts[i] + '\t' + myenv.hostnames[i]
        i=i+1

    return hosts

#修改hostname
@roles('server')
def changeHostname():
    __rootUser()
    hostname=myenv.hostmap[env.host]
#    print hostname
    sudo('echo \'127.0.0.1 '+hostname+'\' >> /etc/hosts')
    sudo('echo '+ hostname+' >/etc/hostname' )
    sudo('hostname '+ hostname)

def downloadJDK():
    pass
#    local('wget --no-check-certificate --no-cookies --header Cookie: oraclelicense=accept-securebackup-cookie http://download.oracle.com/otn-pub/java/jdk/8u73-b02/jdk-8u73-linux-x64.tar.gz')
@roles('server')
def distributeJDK():
    __normalUser()
    print 'will create a temp file /home/username/fabric-jdk.tar.gz'
    env.user=cf.get(activeSession,'newuser')
    env.password=cf.get(activeSession,'passwd')
    put(os.path.join(os.path.split(env.real_fabfile)[0], cf.get(activeSession,'jdk_source_file')), os.path.join('/home',env.user,'fabric-jdk.tar.gz'))
    run('tar -xzf '+ os.path.join('/home',env.user,'fabric-jdk.tar.gz'))
    run('echo "export JAVA_HOME='+os.path.join('/home/',env.user, cf.get(activeSession,'jdk_folder'))+'">>~/.bashrc')
    run("echo 'export PATH=$JAVA_HOME/bin:$PATH' >>~/.bashrc")
    run('rm '+os.path.join('/home',env.user,'fabric-jdk.tar.gz'))

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
    __normalUser()
    run('ls ./')

#免密钥配置,先运行ssh1,再运行ssh2,最后运行ssh3清理
@roles('server')
def ssh1():
    __normalUser()
    with settings(prompts={
        'Enter file in which to save the key (/home/'+env.user+'/.ssh/id_rsa): ': '',
        'Enter passphrase (empty for no passphrase): ': '',
        'Enter same passphrase again: ': '',
        'Overwrite (y/n)? ': 'y'
    }):
        run('ssh-keygen -t rsa ')
        if not os.path.exists(os.path.join(os.path.split(env.real_fabfile)[0], 'files')):
            os.mkdir(os.path.join(os.path.split(env.real_fabfile)[0], 'files'))
        get(os.path.join('/home',env.user,'.ssh/id_rsa.pub'), os.path.join(os.path.split(env.real_fabfile)[0], 'files/'+env.host))

@roles('server')
def ssh2():
    __normalUser()
    for node in myenv.hosts:
        f=fileinput.input(os.path.join(os.path.split(env.real_fabfile)[0], 'files/'+node))
        pem=f.readline()
        f.close()
        run('echo "'+pem+ '" >> ~/.ssh/authorized_keys')
#清理程序
def ssh3():
    for node in myenv.hosts:
        os.remove(os.path.join(os.path.split(env.real_fabfile)[0], 'files/' + node))

#if you only know sudo account password, and you want to configure password-free for root. you have to use this task.
def sudossh1():
    __rootlUser()
    with settings(prompts={
                        'Enter file in which to save the key (/root/.ssh/id_rsa): ': '',
        'Enter passphrase (empty for no passphrase): ': '',
        'Enter same passphrase again: ': '',
        'Overwrite (y/n)? ': 'y'
    }):
        sudo('ssh-keygen -t rsa ')
        sudo('cp /root/.ssh/id_rsa.pub  '+ os.path.join('/home', env.user, '.ssh/id_rsa_for_root.pub'))
        sudo('chmod 644 '+ os.path.join('/home', env.user, '.ssh/id_rsa_for_root.pub'))
        if not os.path.exists(os.path.join(os.path.split(env.real_fabfile)[0], 'files')):
            os.mkdir(os.path.join(os.path.split(env.real_fabfile)[0], 'files'))
        get(os.path.join('/home', env.user, '.ssh/id_rsa_for_root.pub'),
            os.path.join(os.path.split(env.real_fabfile)[0], 'files/' + env.host))

@roles('server')
def sudossh2():
    __rootUser()
    for node in myenv.hosts:
        f=fileinput.input(os.path.join(os.path.split(env.real_fabfile)[0], 'files/'+node))
        pem=f.readline()
        f.close()
        sudo('echo "'+pem+ '" >> /root/.ssh/authorized_keys')


#to enable the bashrc file,we should delete these sentences if they exists:
#case $- in
#    *i *);;
#    * ) return;;
#    esac
#修正bashrc中的问题
@roles('server')
def correct_bashrc():
    __normalUser()
    put(os.path.join(os.path.split(env.real_fabfile)[0], 'correct-bashrc.sh'),os.path.join('/home',env.user,'fabric-tmp.sh'))
    run ('chmod +x '+os.path.join('/home',env.user,'fabric-tmp.sh'))
    run(os.path.join('/home',env.user,'fabric-tmp.sh'))
    run('rm '+os.path.join('/home',env.user,'fabric-tmp.sh'))

#only one server need to install npt server, so remeber change your hosts before run this command
#给机器安装ntp服务端
@roles('server')
def installNTPserver():
    with settings(prompts={
        'Do you want to continue? [Y/n] ':'Y'
    }):
        __rootUser()
        sudo('apt-get install ntp')
        sudo('echo "restrict '+cf.get(activeSession,'ntp_net')+' mask ' +cf.get(activeSession,'ntp_net_mask')+' nomodify " >> /etc/ntp.conf')
        sudo('/etc/init.d/ntp restart')

#设置npt客户端定期任务
@roles('server')
def setNTPtasks():
    __rootUser()
    sudo('echo "#!/bin/bash" >> /etc/cron.daily/myntp')
    sudo('echo "ntpdate '+cf.get(activeSession,'ntp_server')+'" >> /etc/cron.daily/myntp')
    sudo('chmod 755 /etc/cron.daily/myntp')

#重启机器
@roles('server')
def restart():
    __rootUser()
    reboot()

#修改apt-source, will update automatically
@roles('server')
def modifyAptSource():
    __rootUser()
    sudo('mv /etc/apt/sources.list /etc/apt/sources.list_bk')
    for line in open(os.path.join(os.path.split(env.real_fabfile)[0], 'files/sources.list')):
        sudo('echo "'+line+'" >> /etc/apt/sources.list')
    sudo('apt-get update')

#only update apt , do not modify sources.list
@roles('server')
def updateApt():
    __rootUser()
    sudo('apt-get update')

#will modify dns address in /etc/resolvconf/resolv.conf.d/base
@roles('server')
def settingDNS():
    __rootUser()
    for line in open(os.path.join(os.path.split(env.real_fabfile)[0], 'files/dns_address')):
        sudo('echo "' + line + '" >> /etc/resolvconf/resolv.conf.d/base')
    sudo('resolvconf -u')
