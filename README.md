# init_ec2
init EC2 cluster, for free-password-login(ubuntu and root). for hostname, for hosts file.  

##how to use
1. modify passwd.ini
		
		[default]
		activeSession=server #which section is actived
		root = fit #the sudo user, only used for sudo tasks
		passwd = 601tif #passwd of sudoer

		[server] #example of section
		newuser = hxd 	#uesr name, if use createUser task, this user name will be the new user 
		passwd = dxh 		#password of newuser
		hosts=192.168.130.3, 192.168.130.5 #cluster ip
		hostnames=s3, s5 #hostnames of cluster , the number of hostnames must equal with hosts. the hostnames is used for changeHostnames task
		jdk_source_file=files/jdk1.8.77.tar.gz #locally jdk file. the related path is ./
		jdk_folder=jdk1.8.0_77 # when the jdk.tar.gz is unziped, the folder in the tar file.
		[client] #you can define more sections like this.
		newuser = hxd
		passwd = dxh
		hosts = 192.168.130.2
		hostnames = s2
		jdk_source_file=files/jdk1.8.77.tar.gz
		jdk_folder=jdk1.8.0_77
		[all] # and like this
		newuser = hxd
		passwd = dxh
		hosts=192.168.130.2,192.168.130.3, 192.168.130.5, 192.168.130.6, 192.168.130.7, 192.168.130.8, 192.168.130.9, 192.168.130.11, 192.168.130.12, 192.168.130.13, 192.168.130.15, 192.168.130.16, 192.168.130.17, 192.168.130.18, 192.168.130.19, 192.168.130.20
		hostnames=s2,s3, s5, s6, s7, s8, s9, s11, s12, s13, s15, s16, s17, s18, s19, s20
		jdk_source_file=files/jdk1.8.77.tar.gz
		jdk_folder=jdk1.8.0_77		
2. 