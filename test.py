import ConfigParser

cf=ConfigParser.ConfigParser()
cf.read('passwd.ini')
user=cf.get('server','newuser')
print user
print user + 'hxd'