from django.contrib.auth.models import User

from .config import EXTRA_SUPERADMINS


def provision_extra_superadmins(sender, **kwargs):
    """Grant is_superuser to instance-local admins listed in the environment.

    The m2m signal only fires on group membership changes, so these users
    would otherwise never be reconciled.
    """
    if getattr(sender, "label", None) != "documents":
        return

    for username in EXTRA_SUPERADMINS:
        updated = User.objects.filter(username=username, is_superuser=False).update(
            is_superuser=True,
        )
        print(
            f"[casa.superadmins] {username}: {'promoted' if updated else 'already superuser or absent'}"
        )
