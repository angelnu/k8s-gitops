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
| `superadmins.py` | `post_migrate` — full `is_superuser` reconcile |
| `superuser_sync.py` | `m2m_changed` — mirrors the admin SSO group at login |
| `orphan_guard.py` | `post_save` — adopts auxiliary objects created without an owner |
| `catchall_workflow.py` | `post_migrate` + `post_save` — workflow assigning an owner to every consumed document |

## When each handler runs

**Every boot.** The paperless entrypoint runs `manage.py migrate`
unconditionally, and Django emits `post_migrate` even when there is nothing
to apply. That makes it a reliable reconcile point: `provision_groups`,
`provision_extra_superadmins` and `provision_catchall_workflow` all run on
every container start.

This is the only path by which a **config** change takes effect. Changing
`SSO_GROUP_ADMIN` or `PAPERLESS_EXTRA_SUPERADMIN_USERS` requires a pod
restart, not just a re-login, because no user's group membership changes.

**On login.** `sync_superuser` fires from `m2m_changed` when group sync
alters a user's membership. This covers "the user's groups changed in
authentik".

**On first login of a new instance.** `on_user_created` wires the catch-all
workflow, which could not be created earlier because no owner existed yet.

## Rules for changing this app

**`ready()` connects signals. It never writes to the database.** It runs in
every Django process — web, each Celery worker, every `manage.py` invocation
— including during `migrate`, when tables may not exist yet. Django emits a
`RuntimeWarning` for queries at this point; treat it as an error.

**Data writes go in a `post_migrate` receiver.** Every such handler must
guard on `sender.label == "documents"`, or it runs once per migrated app.
Do not connect with `sender=self`: this app has no migrations, so the signal
would never fire.

**Keep `post_migrate` receivers away from the cache.** django-treenode's own
`post_migrate` receiver hits Redis; anything reading tags during migration
fails when Redis is not yet reachable. Restrict handlers to `auth_*` tables,
users, workflows and the auxiliary document models.

**Import paperless models inside `ready()` or inside functions, never at
module level.** At module import time the app registry is not populated.

**Use `Model.objects.filter(...).update(...)` rather than `instance.save()`**
inside signal handlers, to avoid re-entering them.

**Everything must be idempotent.** Handlers run on every container start,
and `migrate` is invoked more than once during the entrypoint. Handlers
print only when something changes, so a steady state is quiet.

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

**Choose `SSO_GROUP_ADMIN` carefully.** It grants full visibility over every
document in the instance. Pointing it at a broad, general-purpose authentik
group means anyone later added to that group silently gains access to all
documents — including on instances belonging to other people.

## Permission model

Group permissions are Django **model** permissions. They do not scope
visibility: django-guardian filters querysets per object, keyed on owner.
Two consequences:

- An object with `owner = NULL` is visible to **every** user holding the
  corresponding view permission. The catch-all workflow and `orphan_guard`
  exist to prevent this.
- No group can "see everything". Only `is_superuser` bypasses the object
  filter, which is why the admin group maps to that flag rather than to a
  wider permission set.

`view_uisettings`, `add_uisettings` and `change_uisettings` are required by
every user including read-only ones; the frontend calls `/api/ui_settings/`
on load and 403s without them.

Tags, correspondents and document types share a single global namespace with
per-object permissions layered on top. Names are unique across the whole
instance, so two tenants cannot each own a tag called "Bank" — the second
consumption reuses the first tenant's object. Objects a user cannot read
still appear as "Private" placeholders in the UI. This is a paperless
limitation with no clean workaround; genuine isolation needs separate
instances.

## Catch-all ownership timing

On a brand-new instance no user exists when `post_migrate` runs, so the
workflow cannot be created — the handler logs and defers. `on_user_created`
wires it as soon as the owner appears, which on a fresh instance is the
first SSO login.

This leaves a window between container start and first login during which a
document arriving through the consumption folder would be ownerless, and
therefore visible to everyone. Accepted: new instances have no scanner
pointed at them yet. If that changes, gate consumption until provisioning
completes.

## Known caveats

- The catch-all workflow covers the consumption folder only. API and web
  uploads need a second trigger of type `DOCUMENT_ADDED`.
- Workflow enum names (`WorkflowTriggerType`, `WorkflowActionType`) have
  changed across paperless versions. Verify against the deployed image
  before editing `catchall_workflow.py`.
- `CustomField` has no `owner` field in current paperless versions, so it is
  excluded from `orphan_guard`. Field *names* are visible to all users;
  field *values* follow their document's permissions.
- `is_staff` is not reconciled. It grants Django admin access at `/admin/`,
  which bypasses SSO entirely — review it manually on internet-exposed
  instances.

## Verifying a deployment

```bash
kubectl logs -n paperless deploy/<instance>-main -c app | grep '\[casa'
```

Handlers print only on change, so a quiet log means the state already
matches. To force a visible run:

```bash
python3 manage.py shell -c "
from django.apps import apps
from casa.groups import provision_groups
from casa.superadmins import provision_extra_superadmins
from casa.catchall_workflow import provision_catchall_workflow
d = apps.get_app_config('documents')
provision_groups(d); provision_extra_superadmins(d); provision_catchall_workflow(d)
"
```

No object should ever be ownerless:

```bash
python3 manage.py shell -c "
from documents.models import Document, Tag, Correspondent, DocumentType, StoragePath, SavedView
for m in (Document, Tag, Correspondent, DocumentType, StoragePath, SavedView):
    print(m.__name__, m.objects.filter(owner__isnull=True).count())
"
```

Current superuser state:

```bash
python3 manage.py shell -c "
from django.contrib.auth.models import User
print([(u.username, u.is_superuser, u.is_staff) for u in User.objects.all()])
"
```