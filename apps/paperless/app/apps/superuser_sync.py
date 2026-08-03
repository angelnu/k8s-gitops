from django.contrib.auth.models import User

from .config import EXTRA_SUPERADMINS, PROTECTED, SSO_GROUP_ADMIN


def sync_superuser(sender, instance, action, **kwargs):
    """Mirror the admin SSO group onto is_superuser at login time."""
    if action not in ("post_add", "post_remove", "post_clear"):
        return
    if not isinstance(instance, User) or instance.username in PROTECTED:
        return

    want = (
        instance.username in EXTRA_SUPERADMINS
        or instance.groups.filter(name=SSO_GROUP_ADMIN).exists()
    )
    if instance.is_superuser != want:
        # update() avoids re-entering signal handlers via save().
        User.objects.filter(pk=instance.pk).update(is_superuser=want)
        print(f"[casa.superuser_sync] {instance.username}: is_superuser -> {want}")
