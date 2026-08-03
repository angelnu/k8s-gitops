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
| `catchall_workflow.py` | `post_migrate` + `post_save` — workflow assigning an owner to every consumed document |

## Rules for changing this app

**`ready()` connects signals. It never writes to the database.** It runs in
every Django process — web, each Celery worker, every `manage.py` invocation
— including during `migrate`, when tables may not exist yet.

**Data writes go in a `post_migrate` receiver.** It fires once per migrated
app, so every handler guards on `sender.label == "documents"` to run exactly
once with the paperless tables present. Do not connect with `sender=self`:
this app has no migrations, so the signal would never fire.

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
| `PAPERLESS_INSTANCE_OWNER` | *(empty)* | Owner for the catch-all workflow; falls back to lowest-pk superuser, then to the first user created |

Group names must match the `groups` claim emitted by the authentik scope
mapping. Group sync itself requires `PAPERLESS_SOCIAL_ACCOUNT_SYNC_GROUPS=true`
on the instance — without it users get no groups and every API call 403s.

## Permission model

Group permissions are Django **model** permissions. They do not scope
visibility: django-guardian filters querysets per object, keyed on document
owner. Two consequences:

- A document with `owner = NULL` is visible to **every** user holding
  `view_document`. The catch-all workflow exists to prevent this.
- No group can "see everything". Only `is_superuser` bypasses the object
  filter, which is why the admin group maps to that flag rather than to a
  wider permission set.

`view_uisettings`, `add_uisettings` and `change_uisettings` are required by
every user including read-only ones; the frontend calls
`/api/ui_settings/` on load and 403s without them.

## Catch-all ownership timing

On a brand-new instance no user exists when `post_migrate` runs, so the
workflow cannot be created — the handler logs and defers. A `post_save`
receiver on `User` wires it as soon as the owner is created, which on a
fresh instance is the first SSO login.

This leaves a window between container start and first login during which a
document arriving through the consumption folder would be ownerless, and
therefore visible to everyone. Accepted: new instances have no scanner
pointed at them yet. If that changes, gate consumption until provisioning
completes.

## Known caveats

- `sync_superuser` only fires when group membership changes. Group sync
  happens at login, so permission changes in authentik require a logout and
  login. This is accepted.
- The catch-all workflow covers the consumption folder only. API and web
  uploads need a second trigger of type `DOCUMENT_ADDED`.
- Workflow enum names (`WorkflowTriggerType`, `WorkflowActionType`) have
  changed across paperless versions. Verify against the deployed image
  before editing `catchall_workflow.py`.

## Verifying a deployment

```bash
kubectl logs -n paperless deploy/<instance>-main -c app | grep '\[casa'
```

Every handler prints a prefixed line. Ownerless documents should always be
zero:

```bash
python3 manage.py shell -c "
from documents.models import Document
print(Document.objects.filter(owner__isnull=True).count())
"
```