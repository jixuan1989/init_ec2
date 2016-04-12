for node in `cat nodes`
do
echo $node
ssh $node "./apache-cassandra-2.2.4/bin/cassandra -p cassandraPID"
done
