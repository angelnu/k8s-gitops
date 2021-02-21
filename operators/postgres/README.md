# postgres namespace

## Zalando postgres operator

[Zalando operator](https://github.com/zalando/postgres-operator) to create highly available databases

* [Operator settings](operator.yaml)

**NOTE:** with version 1.16 the helm chart CDR still has a bug so need to apply lates:
```
kubectl apply -f https://raw.githubusercontent.com/zalando/postgres-operator/master/charts/postgres-operator/crds/postgresqls.yaml
```
Picked 1.6.1 - it should be fixed there already - keeping this until I test with a full K8S redeploy