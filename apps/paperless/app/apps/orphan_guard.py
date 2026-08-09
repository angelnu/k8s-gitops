from django.contrib.auth.models import User

from .config import INSTANCE_OWNER


def _owner():
    if INSTANCE_OWNER:
        return User.objects.filter(username=INSTANCE_OWNER).first()
    return User.objects.filter(is_superuser=True).order_by("pk").first()


def adopt_orphan(sender, instance, created, **kwargs):
    """Assign an owner to auxiliary objects created without one.

    Paperless creates tags, correspondents and document types automatically
    during consumption, and workflows only assign ownership to documents.
    Ownerless objects are visible to every user, so they are adopted here.
    """
    if not created or instance.owner_id is not None:
        return
    owner = _owner()
    if owner is None:
        return
    type(instance).objects.filter(pk=instance.pk).update(owner=owner)
    print(
        f"[casa.orphan] {type(instance).__name__} {instance.pk}: owner -> {owner.username}"
    )
