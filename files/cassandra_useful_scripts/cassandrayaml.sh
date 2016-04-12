source cluster-env.sh
n=`expr ${n} - 1`

tar -xzf apache-cassandra-2.2.5-bin.tar.gz
cd apache-cassandra-2.2.5/conf
sed -i 's/num_tokens:.*/#num_tokens: 256/g' cassandra.yaml
sed -i 's/# initial_token:/initial_token: /g' cassandra.yaml
sed -i 's/concurrent_reads: 32/concurrent_reads: 16/g' cassandra.yaml
sed -i 's/concurrent_writes: 32/concurrent_writes: 16/g' cassandra.yaml
sed -i 's/listen_address: localhost/#listen_address: localhost/g' cassandra.yaml
sed -i 's/# listen_interface: eth0/listen_interface: eth0/g' cassandra.yaml
sed -i 's/rpc_address: localhost/# rpc_address: localhost/g' cassandra.yaml
sed -i 's/# rpc_interface: eth1/rpc_interface: eth0/g' cassandra.yaml
seed=""
seed=${seed}${names}

for (( i=1;i<$n;i++ )); do
#echo ${ips[$i]}
seed=${seed}","${names[$i]}
done
sed -i "s/          - seeds: \"127.0.0.1\"/          - seeds: ${seed}/g" cassandra.yaml


for (( i=0;i<$n;i++ )); do
echo ${ips[$i]}
scp  cassandra.yaml  ${ips[$i]}:./apache-cassandra-2.2.5/conf/
#ssh ${ips[$i]} "sed -i 's/listen_address: localhost/listen_address: ${names[$i]}/g' ./apache-cassandra-2.2.5/conf/cassandra.yaml"
done
