
for node in `cat nodes`
do
echo $node
ssh $node "rm -rf data; mkdir data"
done
