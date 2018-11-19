# -*- coding: utf-8 -*-
import fabfile
from fabric.api import *
from fabric.contrib.files import exists
import os

env = fabfile.env


def __test():
    print fabfile.cf.get('server', 'hosts')

# currently, couchdb is not a cluster. instead, each node is a single instance. so you'd better to just use one node.
# just for ubuntu 14.04, see https://launchpad.net/~couchdb/+archive/ubuntu/stable


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


# only client. you need to install server yourself now.
# (server has too many configurations that need to set. e.g., apache2 or nginx)
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
        run('mkdir '+ cf.get('cassandra','data_folder'))


@roles('server')
def modifyCassandra():
    if (not (env.host in fabfile.cf.get(fabfile.activeSession,'admin_ip'))):
        fabfile.__normalUser()
        cassandra_path = os.path.join('/home', env.user, fabfile.cf.get('cassandra', 'cassandra_folder'))
        yaml = os.path.join(os.path.split(env.real_fabfile)[0], 'files/cassandra.yaml')
        put(yaml, os.path.join(cassandra_path, 'conf/cassandra.yaml'))


@roles('server')
def runOneCassandraSeed():
    if (env.host in fabfile.cf.get('cassandra','one_seed_ip')):
        fabfile.__normalUser()
        cassandra_path=os.path.join('/home',env.user,fabfile.cf.get('cassandra','cassandra_folder'))
        print cassandra_path
        out=run('nohup ' + os.path.join(cassandra_path,'bin/cassandra -p cassandraPID')+' ',pty=True, combine_stderr=True)
        print out


@roles('server')
def runCassandra(status='stop'):
    with settings(warn_only=True):
        fabfile.__normalUser()
        cassandra_path = os.path.join('/home', env.user, fabfile.cf.get('cassandra', 'cassandra_folder'))
        print cassandra_path
        if (status == 'start'):
            if (not (env.host in fabfile.cf.get(fabfile.activeSession,'admin_ip')) and not (env.host in fabfile.cf.get('cassandra','one_seed_ip'))):
                out=run('nohup ' + os.path.join(cassandra_path,'bin/cassandra -p cassandraPID && sleep 5')+' ',pty=True, combine_stderr=True)
                print out
        elif(status=='stop'):
            if (not (env.host in fabfile.cf.get(fabfile.activeSession, 'admin_ip'))):
                pid=run('cat '+os.path.join('/home',env.user,'cassandraPID'))
                run("kill -9 "+pid)
                run('rm '+os.path.join('/home',env.user,'cassandraPID'))
        else:
            print 'unknow command '+ status+", only support start or stop"


@roles('server')
def showCassandra():
    if (env.host in fabfile.cf.get('cassandra', 'one_seed_ip')):
        fabfile.__normalUser()
        cassandra_path = os.path.join('/home', env.user, fabfile.cf.get('cassandra', 'cassandra_folder'))
        out = run(os.path.join(cassandra_path, 'bin/nodetool  status'), pty=True, combine_stderr=True)
        print out


@roles('server')
def rmCassandraData(status='stop'):
    if (not (env.host in fabfile.cf.get(fabfile.activeSession,'admin_ip'))):
        fabfile.__normalUser()
        run('rm -rf '+fabfile.cf.get('cassandra','data_folder'))
        run('mkdir ' + fabfile.cf.get('cassandra', 'data_folder'))


@roles('server')
def distributeHadoop2_8_5():
    if ((not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts):
        fabfile.__normalUser()
        print 'will create a temp file /home/username/fabric-hadoop.tar.gz'
        cf=fabfile.cf
        put(os.path.join(os.path.split(env.real_fabfile)[0], cf.get('hadoop','hadoop_file')), os.path.join('/home',env.user,'fabric-hadoop.tar.gz'))
        run('tar -xzf '+ os.path.join('/home',env.user,'fabric-hadoop.tar.gz'))
        if not remoteFileExist(cf.get('hadoop','data_folder')):
            run('mkdir -p ' + cf.get('hadoop','data_folder'))
        hadoop_config_folder=os.path.join('/home',env.user,cf.get('hadoop','hadoop_folder'),'etc/hadoop')
        with cd(hadoop_config_folder):
            modifyJDK="sed -i 's/export JAVA_HOME=.*/export JAVA_HOME=" + os.path.join('/home/',env.user, cf.get(fabfile.activeSession,'jdk_folder')).replace("/","\\/")  + "/g' hadoop-env.sh"
            run(modifyJDK)
            print '清空slaves...'
            run("cat /dev/null > slaves")

            print '填写slaves...'
            special = cf.get('hadoop','master_ip')
            for node in cf.get('hadoop','slaves').split(","):
                #if(not (node == special and cf.get('hadoop','master_as_a_slave')=="0")):
                    run("echo "+ node + ">> slaves")

            print '填写mapred-site.xml'
            put(os.path.join(os.path.split(env.real_fabfile)[0], 'files/hadoop/mapred-site.xml'),hadoop_config_folder)
            modify="sed -i 's/<value>MASTERIP:10020.*/"+"<value>"+special+":10020<\\/value>"+"/g' mapred-site.xml"
            run(modify)
            modify = "sed -i 's/<value>MASTERIP:19888.*/" + "<value>" + special + ":19888<\\/value>" + "/g' mapred-site.xml"
            run(modify)

            print '填写core-site.xml'
            put(os.path.join(os.path.split(env.real_fabfile)[0], 'files/hadoop/core-site.xml'), hadoop_config_folder)
            modifyFSURL="sed -i 's/<value>.*/"+"<value>hdfs:\\/\\/"+special+":9000<\\/value>"+"/g' core-site.xml"
            run(modifyFSURL)

            print '填写yarn-site.xml'
            put(os.path.join(os.path.split(env.real_fabfile)[0], 'files/hadoop/yarn-site.xml'), hadoop_config_folder)
            modify = "sed -i 's/<value>MASTERIP:8031.*/" + "<value>" + special + ":8031<\\/value>" + "/g' yarn-site.xml"
            run(modify)
            modify = "sed -i 's/<value>MASTERIP:8032.*/" + "<value>" + special + ":8032<\\/value>" + "/g' yarn-site.xml"
            run(modify)
            modify = "sed -i 's/<value>MASTERIP:8030.*/" + "<value>" + special + ":8030<\\/value>" + "/g' yarn-site.xml"
            run(modify)

            print '填写hdfs-site.xml'
            put(os.path.join(os.path.split(env.real_fabfile)[0], 'files/hadoop/hdfs-site.xml'), hadoop_config_folder)
            modify="sed -i 's/<value>DATADIR.*/<value>" + cf.get('hadoop','data_folder').replace("/", "\\/") +"<\\/value>/g' hdfs-site.xml"
            run(modify)
           # modify = "sed -i 's/<value>MASTERIP.*/<value>" + special + ":50090<\\/value>/g' hdfs-site.xml"
            #run(modify)


@roles('server')
def formatHadoop():
    if ((not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts):
        fabfile.__normalUser()
        cf=fabfile.cf
        special = cf.get('hadoop', 'master_public_ip')
        hadoop_folder=os.path.join('/home',env.user,cf.get('hadoop','hadoop_folder'))
        with cd(hadoop_folder):
            if(env.host==special):
                run('bin/hdfs namenode -format '+ cf.get("hadoop",'format_cluster_name'))


@roles('server')
def startHadoop():
    with settings(prompts={
        'Are you sure you want to continue connecting (yes/no)?':'yes'
    }):
        if ((not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts):
            fabfile.__normalUser()
            cf=fabfile.cf
            special = cf.get('hadoop', 'master_public_ip')
            hadoop_folder=os.path.join('/home',env.user,cf.get('hadoop','hadoop_folder'))
            with cd(hadoop_folder):
                if(env.host==special):
                    run('sbin/start-all.sh')
                    run('sbin/mr-jobhistory-daemon.sh start historyserver')


@roles('server')
def stopHadoop():
    if ((not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts):
        fabfile.__normalUser()
        cf=fabfile.cf
        special = cf.get('hadoop', 'master_public_ip')
        hadoop_folder=os.path.join('/home',env.user,cf.get('hadoop','hadoop_folder'))
        with cd(hadoop_folder):
            if(env.host==special):
                run('sbin/stop-all.sh')
                run('sbin/mr-jobhistory-daemon.sh stop historyserver')


def remoteFileExist(file):
    if int(run(" [ -e '"+ file +"' ] && echo 11 || echo 10")) == 11:
        return 1
    else:
        return 0


@roles('server')
def distributeSpark2_4_0():
    if (not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts:
        fabfile.__normalUser()
        print 'will create a temp file /home/username/fabric-spark.tar'
        cf = fabfile.cf
        spark_path = os.path.join('/home', env.user, cf.get('spark', 'spark_folder'))
        spark_config_folder = os.path.join('/home', env.user, cf.get('spark', 'spark_folder'), 'conf')

        put(os.path.join(os.path.split(env.real_fabfile)[0], cf.get('spark', 'spark_file')), os.path.join('/home', env.user, 'fabric-spark.tar'))
        run('tar -xf ' + os.path.join('/home', env.user, 'fabric-spark.tar'))

        if not remoteFileExist(cf.get('spark', 'spark_work')):
            run('mkdir -p ' + cf.get('spark', 'spark_work'))
        with cd(spark_config_folder):
            print '清空slaves...'
            put(os.path.join(os.path.split(env.real_fabfile)[0], 'files/spark/slaves'), spark_config_folder)
            # run("cp slaves.template > slaves")
            run("cat /dev/null > slaves")

            print '填写slaves...'
            # special = cf.get('spark', 'master_ip')
            for node in cf.get('spark', 'slaves').split(","):
                    run("echo " + node + ">> slaves")

            print '填写spark-env.sh'
            put(os.path.join(os.path.split(env.real_fabfile)[0], 'files/spark/spark-env.sh'), spark_config_folder)
            # SPARK_MASTER_PORT
            run("echo 'SPARK_MASTER_PORT=7077' >> spark-env.sh")
            # SPARK_MASTER_HOST
            run("echo 'SPARK_MASTER_HOST=" + cf.get('spark', 'master_ip') + "' >> spark-env.sh")
            # SPARK_LOCAL_IP
            localippara1 = 'ifconfig -a|grep inet|grep -v inet6|grep -v 127|awk '
            localippara2 = '\'{print $2}\''
            localippara3 = '|tr -d '
            localippara4 = '\"addr:\"'
            localippara5 = '|sed -n '
            localippara6 = '\'1p\''
                # SparkLocalIp = run('ifconfig -a|grep inet|grep -v inet6|grep -v 127|awk '{print $2}'|tr -d "addr:"|sed -n '1p'')
            SparkLocalIp = localippara1 + localippara2 + localippara3 + localippara4 + localippara5 + localippara6
            out = run(SparkLocalIp)
            run("echo 'SPARK_LOCAL_IP=" + out + "' >> spark-env.sh")
            # SPARK_HOME
            run("echo 'SPARK_HOME=" + spark_path + "' >> spark-env.sh")
            # JAVA_HOME
            jdk_path=os.path.join('/home/', env.user, cf.get(fabfile.activeSession, 'jdk_folder'))
            run("echo 'JAVA_HOME=" + jdk_path + "' >> spark-env.sh")
            # SPARK_WORK_DIR
            run("echo 'SPARK_WORK_DIR=" + cf.get('spark', 'spark_work') +"' >> spark-env.sh")
            # SPARK_WORKER_OPTS
            spark_work_opts='"-Dspark.worker.cleanup.enabled=true -Dspark.worker.cleanup.interval=1800 -Dspark.worker.cleanup.appDataTtl=3600"'
            run("echo 'SPARK_WORKER_OPTS=" + spark_work_opts + "' >> spark-env.sh")


@roles('server')
def startSpark2_4_0():
    with settings(prompts={
        'Are you sure you want to continue connecting (yes/no)?':'yes'
    }):
        if ((not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts):
            fabfile.__normalUser()
            cf=fabfile.cf
            special = cf.get('spark', 'master_public_ip')
            spark_path = os.path.join('/home', env.user, cf.get('spark', 'spark_folder'))
            with cd(spark_path):
                if(env.host==special):
                    run('sbin/start-all.sh')


@roles('server')
def stopSpark2_4_0():
    if ((not fabfile.myenv.append) or env.host in fabfile.myenv.new_hosts):
        fabfile.__normalUser()
        cf=fabfile.cf
        special = cf.get('spark', 'master_public_ip')
        spark_path = os.path.join('/home', env.user, cf.get('spark', 'spark_folder'))
        with cd(spark_path):
            if(env.host==special):
                run('sbin/stop-all.sh')