import json
import os

from django.contrib.auth.models import Group, Permission, User

BASE = [
    "add_uisettings",
    "change_uisettings",
    "view_uisettings",
    "view_paperlesstask",
]

DOC_MODELS = [
    "document",
    "tag",
    "correspondent",
    "documenttype",
    "storagepath",
    "customfield",
    "savedview",
    "note",
    "sharelink",
    "paperlesstask",
]

DEFAULT_SPEC = {
    os.environ.get("CASA_READER_GROUP", "casa96"): {
        "models": DOC_MODELS,
        "actions": ["view"],
    },
    os.environ.get("CASA_EDITOR_GROUP", "casa_editors"): {
        "models": DOC_MODELS,
        "actions": ["view", "add", "change", "delete"],
    },
}

ADMIN_GROUP = os.environ.get("CASA_ADMIN_GROUP", "casa_admins")
PROTECTED = set(
    filter(None, os.environ.get("CASA_PROTECTED_USERS", "admin").split(","))
)


def provision_groups(sender, **kwargs):
    spec = json.loads(os.environ.get("CASA_GROUPS", "{}")) or DEFAULT_SPEC

    # El grupo de admins no necesita permisos de modelo: is_superuser los cubre.
    for name in list(spec) + [ADMIN_GROUP]:
        cfg = spec.get(name)
        if cfg is None:
            Group.objects.get_or_create(name=name)
            print(f"[casa] {name}: grupo sin permisos de modelo")
            continue

        codenames = BASE + [f"{a}_{m}" for m in cfg["models"] for a in cfg["actions"]]
        perms = Permission.objects.filter(
            content_type__app_label="documents",
            codename__in=codenames,
        )
        missing = set(codenames) - set(perms.values_list("codename", flat=True))
        group, created = Group.objects.get_or_create(name=name)
        group.permissions.set(perms)
        print(
            f"[casa] {name}: {'creado' if created else 'actualizado'}, {perms.count()} permisos"
        )
        if missing:
            print(f"[casa] AVISO {name}: sin coincidencia para {sorted(missing)}")


def sync_superuser(sender, instance, action, **kwargs):
    if action not in ("post_add", "post_remove", "post_clear"):
        return
    if not isinstance(instance, User) or instance.username in PROTECTED:
        return

    want = instance.groups.filter(name=ADMIN_GROUP).exists()
    if instance.is_superuser != want:
        User.objects.filter(pk=instance.pk).update(is_superuser=want)
        print(f"[casa] {instance.username}: is_superuser -> {want}")
