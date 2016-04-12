~/apache-cassandra-2.2.4/bin/cqlsh pc17 -f ~/dumplog1.sql >logs/$1_event
~/apache-cassandra-2.2.4/bin/cqlsh pc17 -f ~/dumplog2.sql >logs/$1_session

