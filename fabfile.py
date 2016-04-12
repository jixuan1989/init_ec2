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
    new_hosts=[]
    new_hostnames=[]
    new_hostmap={}
    existed_hosts=[]
    existed_hostnames=[]
    existed_hostmap={}
    append=False


myenv=__MyEnv()
myenv.hosts=map(__lambdastrp, cf.get(activeSession,'hosts').split(','))
myenv.hostnames=map(__lambdastrp,cf.get(activeSession,'hostnames').split(','))

i=0
while i<len(myenv.hosts):
    myenv.hostmap[myenv.hosts[i]]=myenv.hostnames[i]
    i=i+1


if(len(cf.get(activeSession,'existed_hosts'))!=0):
    myenv.append=True
    myenv.existed_hosts=map(__lambdastrp, cf.get(activeSession,'existed_hosts').split(','))
    myenv.existed_hostnames = map(__lambdastrp, cf.get(activeSession, 'existed_hostnames').split(','))
    i = 0
    while i < len(myenv.existed_hosts):
        myenv.existed_hostmap[myenv.existed_hosts[i]] = myenv.existed_hostnames[i]
        i = i + 1

    myenv.new_hosts=myenv.hosts[:]
    myenv.new_hostnames=myenv.hostnames[:]
    myenv.new_hostmap=myenv.hostmap.copy()

    for a in myenv.existed_hosts:
        myenv.new_hosts.remove(a)
        myenv.new_hostmap.pop(a)
    for a in myenv.existed_hostnames:
        myenv.new_hostnames.remove(a)

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
            if((not myenv.append) or env.host in myenv.new_hosts):
                sudo('adduser '+cf.get(activeSession,'newuser') ,pty=True, combine_stderr=True)
            else:
                print "skip existed node:" + env.host
#批量删除用户
@roles('server')
def removeUser():
    __rootUser()
    if ((not myenv.append) or env.host in myenv.new_hosts):
        sudo('deluser '+ cf.get(activeSession,'newuser'), pty=True, combine_stderr=True)
    else:
        print "skip existed node:" +env.host
#修改hosts
@roles('server')
def addIntoHostFile():
    __rootUser()
    if ((not myenv.append) or env.host in myenv.new_hosts):
        sudo('echo "' + __generateHosts() + '" >> /etc/hosts')
    else:
        sudo('echo "' + __generateNewHosts() + '" >> /etc/hosts')


def __generateHosts():
    hosts = ''
    i = 0
    size = len(myenv.hosts)
    while i < size:
        hosts = hosts + '\n' + myenv.hosts[i] + '\t' + myenv.hostnames[i]
        i = i + 1
    return hosts

def __generateNewHosts():
    hosts=''
    i=0
    size=len(myenv.new_hosts)
    while i<size:
        hosts = hosts + '\n' + myenv.new_hosts[i] + '\t' + myenv.new_hostnames[i]
        i=i+1
    return hosts




#修改hostname
@roles('server')
def changeHostname():
    __rootUser()
    if ((not myenv.append) or env.host in myenv.new_hosts):
        hostname=myenv.hostmap[env.host]
        #print hostname
        sudo('echo \'127.0.0.1 '+hostname+'\' >> /etc/hosts')
        sudo('echo '+ hostname+' >/etc/hostname' )
        sudo('hostname '+ hostname)
    else:
        print "skip existed node:" + env.host
#def downloadJDK():
#    pass
#    local('wget --no-check-certificate --no-cookies --header Cookie: oraclelicense=accept-securebackup-cookie http://download.oracle.com/otn-pub/java/jdk/8u73-b02/jdk-8u73-linux-x64.tar.gz')
@roles('server')
def distributeJDK():
    __normalUser()
    if ((not myenv.append) or env.host in myenv.new_hosts):
        print 'will create a temp file /home/username/fabric-jdk.tar.gz'
        env.user=cf.get(activeSession,'newuser')
        env.password=cf.get(activeSession,'passwd')
        put(os.path.join(os.path.split(env.real_fabfile)[0], cf.get(activeSession,'jdk_source_file')), os.path.join('/home',env.user,'fabric-jdk.tar.gz'))
        run('tar -xzf '+ os.path.join('/home',env.user,'fabric-jdk.tar.gz'))
        run('echo "export JAVA_HOME='+os.path.join('/home/',env.user, cf.get(activeSession,'jdk_folder'))+'">>~/.bashrc')
        run("echo 'export PATH=$JAVA_HOME/bin:$PATH' >>~/.bashrc")
        run('rm '+os.path.join('/home',env.user,'fabric-jdk.tar.gz'))
    else:
        print "skip existed node:" + env.host

@roles('server')
def __test3():
    env.user=cf.get('client','newuser')
    env.password=cf.get('client','passwd')
    test2()

def __test2():
        run('ls ./')

@roles('test')
def __test():
    with settings(warn_only=True):
        cd('/')
        run('ls ./')
        #result = local('./manage.py test my_app', capture=True)
        #if result.failed and not confirm("Tests failed. Continue anyway?"):
        #    abort("Aborting at user request.")

def __test4():
    a=cf.get('client','hosts')
    a=a.split(',')
    print type(a)
    print a

@roles('server')
def __test5():
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
        if ((not myenv.append) or env.host in myenv.new_hosts):
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
        if((not myenv.append) or env.host in myenv.new_hosts or node in myenv.new_hosts):
            run('echo "'+pem+ '" >> ~/.ssh/authorized_keys')

#清理程序
def ssh3():
    for node in myenv.hosts:
        os.remove(os.path.join(os.path.split(env.real_fabfile)[0], 'files/' + node))

#if you only know sudo account password, and you want to configure password-free for root. you have to use this task.
@roles('server')
def sudossh1():
    __rootUser()
    with settings(prompts={
                        'Enter file in which to save the key (/root/.ssh/id_rsa): ': '',
        'Enter passphrase (empty for no passphrase): ': '',
        'Enter same passphrase again: ': '',
        'Overwrite (y/n)? ': 'y'
    }):
        if ((not myenv.append) or env.host in myenv.new_hosts):
            sudo('ssh-keygen -t rsa ')
        sudo('cp /root/.ssh/id_rsa.pub  '+ os.path.join('/home', env.user, 'id_rsa_for_root.pub'))
        sudo('chmod 644 '+ os.path.join('/home', env.user, 'id_rsa_for_root.pub'))
        if not os.path.exists(os.path.join(os.path.split(env.real_fabfile)[0], 'files')):
            os.mkdir(os.path.join(os.path.split(env.real_fabfile)[0], 'files'))
        get(os.path.join('/home', env.user, 'id_rsa_for_root.pub'),
            os.path.join(os.path.split(env.real_fabfile)[0], 'files/' + env.host))
        sudo('rm '+ os.path.join('/home', env.user, 'id_rsa_for_root.pub'))
@roles('server')
def sudossh2():
    __rootUser()
    for node in myenv.hosts:
        f=fileinput.input(os.path.join(os.path.split(env.real_fabfile)[0], 'files/'+node))
        pem=f.readline()
        f.close()
        if ((not myenv.append) or env.host in myenv.new_hosts or node in myenv.new_hosts):
            sudo('echo "' + pem + '" >> /root/.ssh/authorized_keys')



#to enable the bashrc file,we should delete these sentences if they exists:
#case $- in
#    *i *);;
#    * ) return;;
#    esac
#修正bashrc中的问题
@roles('server')
def correct_bashrc():
    __normalUser()
    if ((not myenv.append) or env.host in myenv.new_hosts):
        put(os.path.join(os.path.split(env.real_fabfile)[0], 'correct-bashrc.sh'),os.path.join('/home',env.user,'fabric-tmp.sh'))
        run ('chmod +x '+os.path.join('/home',env.user,'fabric-tmp.sh'))
        run(os.path.join('/home',env.user,'fabric-tmp.sh'))
        run('rm '+os.path.join('/home',env.user,'fabric-tmp.sh'))
    else:
        print "skip existed node:" + env.host
#only one server need to install npt server, so remeber change your hosts before run this command
#给机器安装ntp服务端
@roles('server')
def installNTPserver(multi='n'):
    with settings(prompts={
        'Do you want to continue? [Y/n] ':'Y'
    }):
        if(len(env.hsots)>1 and multi!='y'):
            print "if you are sure that you want to install NTP server on multi servers, please use `fab installNTPserver:y`"
            return
        else:
            __rootUser()
            if ((not myenv.append) or env.host in myenv.new_hosts):
                sudo('apt-get install ntp')
                sudo('echo "restrict '+cf.get(activeSession,'ntp_net')+' mask ' +cf.get(activeSession,'ntp_net_mask')+' nomodify " >> /etc/ntp.conf')
                sudo('/etc/init.d/ntp restart')
            else:
                print "skip existed node:" + env.host
#设置npt客户端定期任务
@roles('server')
def setNTPtasks():
    __rootUser()
    if ((not myenv.append) or env.host in myenv.new_hosts):
        sudo('echo "#!/bin/bash" >> /etc/cron.daily/myntp')
        sudo('echo "ntpdate '+cf.get(activeSession,'ntp_server')+'" >> /etc/cron.daily/myntp')
        sudo('chmod 755 /etc/cron.daily/myntp')
    else:
        print "skip existed node:" + env.host

#重启机器
@roles('server')
def restart():
    __rootUser()
    if ((not myenv.append) or env.host in myenv.new_hosts):
        reboot()
    else:
        print "skip existed node:" + env.host
#修改apt-source, will update automatically
@roles('server')
def modifyAptSource():
    __rootUser()
    if ((not myenv.append) or env.host in myenv.new_hosts):
        sudo('mv /etc/apt/sources.list /etc/apt/sources.list_bk')
        for line in open(os.path.join(os.path.split(env.real_fabfile)[0], 'files/sources.list')):
            sudo('echo "'+line+'" >> /etc/apt/sources.list')
        sudo('apt-get update')
    else:
        print "skip existed node:" + env.host

#only update apt , do not modify sources.list
@roles('server')
def updateApt():
    __rootUser()
    if ((not myenv.append) or env.host in myenv.new_hosts):
        sudo('apt-get update')

#will modify dns address in /etc/resolvconf/resolv.conf.d/base
@roles('server')
def settingDNS():
    __rootUser()
    if ((not myenv.append) or env.host in myenv.new_hosts):
        for line in open(os.path.join(os.path.split(env.real_fabfile)[0], 'files/dns_address')):
            sudo('echo "' + line + '" >> /etc/resolvconf/resolv.conf.d/base')
        sudo('resolvconf -u')
    else:
        print "skip existed node:" + env.host
#挂载磁盘
@roles('server')
def addDisk(device,location):
    __rootUser()
    if ((not myenv.append) or env.host in myenv.new_hosts):
        sudo('mkdir ' + location)
        with settings(prompts={
            'Proceed anyway? (y,n) ': 'y'
        }):
            #print device
            #print location
            sudo('mkfs -t ext4 ' + device)
            sudo('mount -t ext4 ' + device +  ' ' + location)
            sudo('chmod -R 777 ' + location)
            sudo('echo "'+"#"+device+'">>/etc/fstab')
            sudo("echo " +"'UUID='`blkid|grep sdb|awk '{print $2}'|awk -F '\"' '{print $2}'`"+"\t"+location+"\t ext4"+"\tdefaults\t0\t3 >>/etc/fstab")
    else:
        print "skip existed node:" +env.host