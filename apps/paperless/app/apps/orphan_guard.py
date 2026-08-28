from django.contrib.auth.models import User
from django.db import transaction

from .config import INSTANCE_OWNER


def _owner():
    if INSTANCE_OWNER:
        return User.objects.filter(username=INSTANCE_OWNER).first()
    return User.objects.filter(is_superuser=True).order_by("pk").first()


def _adopt(model, pk):
    """Assign an owner if the object still exists and is still ownerless."""
    obj = model.objects.filter(pk=pk, owner__isnull=True).first()
    if obj is None:
        return
    owner = _owner()
    if owner is None:
        print(f"[casa.orphan] {model.__name__} {pk}: no owner resolved")
        return
    model.objects.filter(pk=pk).update(owner=owner)
    print(f"[casa.orphan] {model.__name__} {pk}: owner -> {owner.username}")


def adopt_orphan(sender, instance, created, **kwargs):
    """Assign an owner to auxiliary objects created without one.

    Paperless creates tags, correspondents and document types automatically
    during consumption, and workflows only assign ownership to documents.
    Ownerless objects are visible to every user.

    Deferred to commit so a rolled-back consumption does not leave a write
    against a row that no longer exists, and so any owner assigned by a
    workflow in the same transaction wins over ours.
    """
    if not created or instance.owner_id is not None:
        return
    transaction.on_commit(lambda: _adopt(type(instance), instance.pk))


def adopt_orphan_document(sender, instance, created, **kwargs):
    """Backstop for documents that no workflow claimed.

    The catch-all workflow covers the consumption folder and (with the
    DOCUMENT_ADDED trigger) web and API uploads, but this catches anything
    that slips through either path. An ownerless document is readable by
    every user holding view_document, so this is the invariant that matters
    most.
    """
    if not created:
        return
    transaction.on_commit(lambda: _adopt(type(instance), instance.pk))
