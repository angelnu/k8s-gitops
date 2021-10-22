# postgres namespace

## Zalando postgres operator

[Zalando operator](https://github.com/zalando/postgres-operator) to create highly available databases

* [Operator settings](operator.yaml)

## Status of all clusters

`kubectl get pods -o name | grep postgres-0 | xargs -I{} kubectl exec {} -- patronictl list`

## Repair HowTo

- patroni manages the cluster
  - `patronictl list` - list member and status
  - `patronictl reinit <cluster> <member>` - reinit broken node
- in-place upgrade: `su postgres -c "python3 /scripts/inplace_upgrade.py 2"`
- cannot re-create DB cluster: `kubectl delete poddisruptionbudgets postgres-<chart name>-zalando-postgres-cluster-postgres-pdb`
- apply backup:
  1. get into LEADER postgres node
  2. delete old DB: 
     ```
     psql -U postgres -c 'drop database "tt-rss"'
     ```
  2. `apt update && apt install -y openssh-client`
  3. `rsync anunez@nas:/volume1/kubernetes/backup/db/tt-rss/backup .`
  4. `psql -U postgres -f backup`
- list status of all clusters:
  - `kubectl get pods -o name | grep postgres-0 | xargs -I{} kubectl exec {} -- patronictl list`

