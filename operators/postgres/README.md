# postgres namespace

## Zalando postgres operator

[Zalando operator](https://github.com/zalando/postgres-operator) to create highly available databases

* [Operator settings](operator.yaml)

## Repair HowTo

- patroni manages the cluster
  - `patronictl list` - list member and status
  - `patronictl reinit <cluster> <member>` - reinit broken node


