# postgres namespace

## Zalando postgres operator

[Zalando operator](https://github.com/zalando/postgres-operator) to create highly available databases

* [Operator settings](operator.yaml)

## Repair HowTo

- patroni manages the cluster
  - `patronictl list` - list member and status
  - `patronictl reinit <cluster> <member>` - reinit broken node
- in-place upgrade: `su postgres -c "python3 /scripts/inplace_upgrade.py 2"`
- cannot re-create DB cluster: `kubectl delete poddisruptionbudgets postgres-<chart name>-zalando-postgres-cluster-postgres-pdb`
- apply backup:
  1. get into postgres node
  2. `apt update && apt install openssh-client`
  3. `rsync anunez@nas:/volume1/kubernetes/backup/db/tt-rss/backup .`
  4. `psql -U postgres -f backup`


