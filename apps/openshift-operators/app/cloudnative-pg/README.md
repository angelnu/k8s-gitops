# Cloudnative Postgres operator

## Manual dump & recovery
kubectl exec -n app app-db-2 --   pg_dump -d app -U postgres > app-backup
kubectl exec -n app -ti app-db-1 -- psql -U postgres -d app < app-backup