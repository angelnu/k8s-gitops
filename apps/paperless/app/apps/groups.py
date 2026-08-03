from django.contrib.auth.models import Group, Permission

from .config import BASE_PERMS, SPEC


def provision_groups(sender, **kwargs):
    """Create the SSO-backed groups and pin their model permissions."""
    if getattr(sender, "label", None) != "documents":
        return

    for name, cfg in SPEC.items():
        group, created = Group.objects.get_or_create(name=name)

        if cfg is None:
            print(
                f"[casa.groups] {name}: {'created' if created else 'exists'}, no model perms"
            )
            continue

        codenames = BASE_PERMS + [
            f"{a}_{m}" for m in cfg["models"] for a in cfg["actions"]
        ]
        perms = Permission.objects.filter(
            content_type__app_label="documents",
            codename__in=codenames,
        )
        # Surface typos and renamed models here instead of as a 403 later.
        missing = set(codenames) - set(perms.values_list("codename", flat=True))
        group.permissions.set(perms)
        print(
            f"[casa.groups] {name}: {'created' if created else 'updated'}, {perms.count()} perms"
        )
        if missing:
            print(f"[casa.groups] WARNING {name}: no match for {sorted(missing)}")
