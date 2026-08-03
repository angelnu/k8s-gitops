# casa — Paperless-ngx provisioning app

A minimal Django app injected into paperless-ngx to provision groups,
permissions, superuser status and the catch-all ownership workflow.
Replaces an earlier bootstrap Job.

## Why an app and not a Job

The initContainer approach deadlocked: paperless runs Redis as a sidecar,
sidecars do not start until initContainers exit, and Django's `post_migrate`
signal reaches Redis via django-treenode. A Helm hook Job worked but, on
SQLite, mounting the shared data volume in a second pod triggered SELinux
MCS relabeling on OKD and locked the running app out of its own database.

Running inside the app process avoids both: same process, same volume, same
SELinux label, correct ordering by construction.

## How it is wired

The ConfigMap generated here is mounted at
`/usr/src/paperless/src/casa`, which is already on Python's path. The app is
registered by appending `casa` to `PAPERLESS_APPS` in the HelmRelease:

```yaml
env:
  PAPERLESS_APPS: "allauth.socialaccount.providers.openid_connect,casa"
```

`PAPERLESS_APPS` is a list — do not drop the allauth provider.

## Files

| File | Responsibility |
|---|---|
| `apps.py` | `AppConfig.ready()` — connects signals only, no DB writes |
| `config.py` | All environment reads and the permission spec |
| `groups.py` | `post_migrate` — creates SSO groups, pins model permissions |
| `superadmins.py` | `post_migrate` — promotes users from `PAPERLESS_EXTRA_SUPERADMIN_USERS` |
| `superuser_sync.py` | `m2m_changed` — mirrors the admin SSO group onto `is_superuser` |
| `catchall_workflow.py` | `post_migrate` — workflow assigning an owner to every consumed document |

## Rules for changing this app

**`ready()` connects signals. It never writes to the database.** It runs in
every Django process — web, each Celery worker, every `manage.py` invocation
— including during `migrate`, when tables may not exist yet.

**Data writes go in a `post_migrate` receiver.** It fires once, after
migrations, with tables present.

**Keep `post_migrate` receivers away from the cache.** django-treenode's own
`post_migrate` receiver hits Redis; anything reading tags during migration
will fail when Redis is not yet reachable. Restrict handlers to
`auth_*` tables, users and workflows.

**Import paperless models inside functions, not at module level.** At import
time the app registry is not ready.

**Use `User.objects.filter(...).update(...)` rather than `instance.save()`**
inside signal handlers, to avoid re-entering them.

**Everything must be idempotent.** Handlers run on every container start.
`get_or_create` plus `set()` is the pattern used throughout.

**An `ImportError` here CrashLoops paperless.** The app is in
`INSTALLED_APPS`. Test on the `test` cluster before `prod`.

**Add new files to `kustomization.yaml`.** A file missing from the
ConfigMap is an `ImportError` at startup.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `SSO_GROUP_READER` | `casa_readers` | Group granted view-only model perms |
| `SSO_GROUP_WRITER` | `casa_editors` | Group granted full document CRUD |
| `SSO_GROUP_ADMIN` | `casa_admins` | Membership implies `is_superuser` |
| `PAPERLESS_EXTRA_SUPERADMIN_USERS` | *(empty)* | CSV of per-instance superadmins, no authentik group needed |
| `PAPERLESS_PROTECTED_USERS` | `admin` | CSV of accounts the superuser reconcile never touches |
| `PAPERLESS_INSTANCE_OWNER` | *(empty)* | Owner for the catch-all workflow; falls back to lowest-pk superuser |