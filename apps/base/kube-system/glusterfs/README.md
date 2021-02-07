# Glusterfs Cluster

This setup need to be moved into a Helm chart or replaced with a different solution since Heketi is deprecated.

## Bootstrap

0. ensure the information on `configmap-kube-system-gusterfs-initial-config.yaml` matches the nodes
0. disable gluster for DB volume (so it starts) in hekiti.yaml
1. exec into container
   ```
   heketi-cli topology load --json=/etc/heketi/topology/all.json
   heketi-cli setup-openshift-heketi-storage
   ```
2. 
4. kubectl cp heketi-74d7879c78-z6dqb:heketi-storage.json services/kube-system/glusterfs/heketi-storage.json
5. kubectl apply -f services/kube-system/glusterfs/heketi-storage.json
6. Remove the job of services/kube-system/glusterfs/heketi-storage.json to avoid overwriting the DB next time I re-deploy the services

7. Re-add gluster for DB volume