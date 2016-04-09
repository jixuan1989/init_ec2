# init_ec2
This project helps users to initialize a new cluster.

It is suitable for:
 
 * a real cluster, which consists of PCs, small servers or other  physical machines you own.
 * cloud environment, such as Amazon EC2, aliyun. 

The only conditions you should have are:

- you have installed ubuntu (tested on 14.04) OS on all the nodes. (it is always eligibly in cloud environments, e.g., EC2, aliyun)
- you  know or have set the ip address on each node. 
- **python 2.7** has been installed on your laptop/PC. (unless you use a Windows OS, otherwise you are eligibly. on Windows, you need to install Python yourself)
- **fabric** (version >=1.10) has been installed on your laptop/PC
	- it seems a little harder than above steps. But believe me, you deserve it! 
	- on Mac, install easy_install and then fabric:
		- download file https://pypi.python.org/pypi/ez_setup 
		- sudo python ez_setup.py
		- sudo easy_install fabric
	- on Linux (Ubuntu), the same way (notice, do not use pip to install fabric, you will be disappointed; besides, apt-get install fabric is ok, but the version is 1.8 now (2016.4))
		- sudo apt-get install python-setuptools python-dev build-essential
		- sudo easy_install fabric
	- on Windows,... Good luck, guy. I have not tried how to install fabric on Windows. But it should not be a probelm.  
init EC2 cluster, for free-password-login(ubuntu and root). for hostname, for hosts file.  

##how to use
1. modify passwd.ini
 
    this is an example
		
		[default]
		#which section is actived
		activeSession=
		#the sudo user, only used for sudo tasks
		root =
		#passwd of sudoer
		passwd =
		
		#example of section
		[server]
		#uesr name, if use createUser task, this user name will be the new user
		newuser =
		#password of newuser
		passwd =
		#cluster ips, use comma to split
		hosts=
		#hostnames of cluster , the number of hostnames must equal with hosts. the hostnames is used for changeHostname tass
		hostnames=
		#locally jdk file. the related path is ./
		jdk_source_file=
		# when the jdk.tar.gz is unziped, the folder in the tar file.
		jdk_folder=
		# the ntp server address you  want to sync
		ntp_server=
		# the allowed net that can sync with your ntp server
		ntp_net=
		# the allowed net mask that can sync with your ntp server
		ntp_net_mask=
		
	this is an instance:
	
		[default]
		activeSession=server
		root = fit
		passwd =111
		
		[server]
		newuser = hxd
		passwd = 1112
		hosts=192.168.130.3, 192.168.130.5		hostnames=s3, s5, 
		jdk_source_file=files/jdk1.8.77.tar.gz
		jdk_folder=jdk1.8.0_77
		ntp_server=192.168.130.2
		[client]
		newuser = hxd
		passwd = 1112
		hosts = 192.168.130.2
		hostnames = s2
		jdk_source_file=files/jdk1.8.77.tar.gz
		jdk_folder=jdk1.8.0_77
		ntp_net=192.168.130.0
		ntp_net_mask=255.255.255.0
		ntp_server=192.168.130.2
		[all]
		newuser = hxd
		passwd = 1112
		hosts=192.168.130.2,192.168.130.3, 192.168.130.5
		hostnames=s2,s3, s5
		jdk_source_file=files/jdk1.8.77.tar.gz
		jdk_folder=jdk1.8.0_77
2. you can use this script like this 
   
   `fab task_name` 
   
   you can use `fab help` to show how many tasks supportted.
   
   current supportted tasks:
   
    * createUser
        - create a new user (username is 'newuser' in the configurations, password is 'passwd' in the active configurations).
    * removeUser
    	- delete the user we created
    * addIntoHostFile
    	- add all the <ip,hostname> into /etc/hosts
    * changeHostname
    	- change all the hostnames as the values in the actived conf.
    * installnptserver
    	- install ntp server on nodes. We suggest you only install ntp server on one node in the cluster, instead of all the nodes.(how to do: enable a configruation which has only one ip in 'hosts')
    * distributeJDK
    	- after you manual download a jdk file, you can use this task to push it to all the nodes and modify the $JAVA_HOME and $PATH 
    * setnpttaks
    	- add a scheduled task every day for ntpdate time with the ntp server
    * password-free ssh
    	- setting password-free ssh. how to use: 
    		- fab ssh1  (this can generate pem files)
    		- fab ssh2  (this finish the password-free)
    		- fab ssh3  (cleanup)
    * restart
    	- reboot the cluster
    * correct_bashrc
    	- normally, we use `ssh hxd@node1 "jps"`, the terminal says: jps command not found, though we have set $JAVA_HOME and $PATH in .bashrc file. The reason is that .bashrc is ignored when we run a non-interactive login command. To solve that, use this task to repair the bashrc file.
    * modifyAtpSource
    	- modify the apt sources.list as files/sources.list.
    * addDisk
    	- when you add a new disk, you should format it and then mount it. this task help you. use `fab addDisk:device,location`. e.g., `fab addDisk:/dev/sdb,/datab`
    * TODO: we will add new tasks to help user add new nodes in an existed cluster    	
 
##Amazon Ec2 (or other pem based ssh)
in Amazon Ec2, we use a pem file to login instead of password.

To use the script on Amazon EC2. you need modify the script now. But do not worry, just a little thing you need to do:

* comment "env.password=..." in rootUser() 
* add env.key_filename=['filepath'] in rootUser()
* Cheers! 

 