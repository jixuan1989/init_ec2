#!/bin/bash
tokens=(
-5534023222112865486
-1844674407370955164
1844674407370955158
5534023222112865480
9223372036854775802
)
ips=(pc17 pc19 pc21 pc23 pc25)
for (( i=0; i<5; i++)); do 
echo ${ips[$i]}
echo ${tokens[$i]}
ssh ${ips[$i]} "sed -i 's/initial_token:.*/initial_token: ${tokens[$i]}/g' /home/quovis/apache-cassandra-2.2.4/conf/cassandra.yaml"
done 

