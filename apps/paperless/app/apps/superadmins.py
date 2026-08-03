from django.contrib.auth.models import User

from .config import EXTRA_SUPERADMINS, PROTECTED, SSO_GROUP_ADMIN


def provision_extra_superadmins(sender, **kwargs):
    """Reconcile is_superuser across every user at container start.

    Two sources grant it: membership of SSO_GROUP_ADMIN, and the per-instance
    PAPERLESS_EXTRA_SUPERADMIN_USERS list.

    This full pass is needed because sync_superuser only fires when group
    membership *changes*. A user whose membership already matched when
    SSO_GROUP_ADMIN was introduced would otherwise never be reconciled, no
    matter how many times they log out and back in.
    """
    if getattr(sender, "label", None) != "documents":
        return

    for user in User.objects.exclude(username__in=PROTECTED):
        want = (
            user.username in EXTRA_SUPERADMINS
            or user.groups.filter(name=SSO_GROUP_ADMIN).exists()
        )
        if user.is_superuser != want:
            # update() avoids re-entering signal handlers via save().
            User.objects.filter(pk=user.pk).update(is_superuser=want)
            print(f"[casa.superadmins] {user.username}: is_superuser -> {want}")

    # Listed users may not exist yet on a fresh instance; report either way.
    for username in EXTRA_SUPERADMINS:
        if not User.objects.filter(username=username).exists():
            print(f"[casa.superadmins] {username}: listed but not present yet")
