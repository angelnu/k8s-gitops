from django.contrib.auth.models import User
from django.db import transaction

from .config import EXTRA_SUPERADMINS, PROTECTED, SSO_GROUP_ADMIN


def _reconcile(pk):
    """Re-read the user's final group state and apply is_superuser.

    Must re-fetch: the instance captured by the signal has a stale group
    cache from before the change.
    """
    user = User.objects.filter(pk=pk).first()
    if user is None:
        return

    want = (
        user.username in EXTRA_SUPERADMINS
        or user.groups.filter(name=SSO_GROUP_ADMIN).exists()
    )
    if user.is_superuser != want:
        User.objects.filter(pk=pk).update(is_superuser=want)
        print(f"[casa.superuser_sync] {user.username}: is_superuser -> {want}")


def sync_superuser(sender, instance, action, **kwargs):
    """Mirror the admin SSO group onto is_superuser at login time.

    Group sync calls groups.set(), which clears then re-adds. Acting on the
    intermediate post_clear state demotes the user, and a login that fails
    between clear and add leaves them demoted with no groups — locking out
    the last admin. Deferring to transaction commit means only the final
    state is ever seen, and a rolled-back login applies nothing.
    """
    if action not in ("post_add", "post_remove", "post_clear"):
        return
    if not isinstance(instance, User) or instance.username in PROTECTED:
        return

    transaction.on_commit(lambda: _reconcile(instance.pk))
