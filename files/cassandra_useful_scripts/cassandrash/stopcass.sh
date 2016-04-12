
for node in `cat nodes`
do
echo $node
ssh $node "cat cassandraPID| xargs kill "
done
