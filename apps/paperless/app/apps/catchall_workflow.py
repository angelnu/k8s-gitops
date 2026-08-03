from django.contrib.auth.models import User

from .config import INSTANCE_OWNER


def _resolve_owner():
    """Return the user that should own otherwise-ownerless documents."""
    if INSTANCE_OWNER:
        return User.objects.filter(username=INSTANCE_OWNER).first()
    return User.objects.filter(is_superuser=True).order_by("pk").first()


def provision_catchall_workflow(sender, **kwargs):
    """Ensure no document can be consumed without an owner.

    Ownerless documents are visible to every user, so this is the safety net.
    It sorts first; per-folder workflows run afterwards and override the owner.
    """
    # Imported here: at module level this would run before the app registry
    # is ready.
    from documents.models import Workflow, WorkflowAction, WorkflowTrigger

    owner = _resolve_owner()
    if owner is None:
        print("[casa.catchall] WARNING: no owner resolved, skipping")
        return

    trigger, _ = WorkflowTrigger.objects.get_or_create(
        type=WorkflowTrigger.WorkflowTriggerType.CONSUMPTION,
        filter_path="*",
    )
    action, _ = WorkflowAction.objects.get_or_create(
        type=WorkflowAction.WorkflowActionType.ASSIGNMENT,
        assign_owner=owner,
    )
    workflow, created = Workflow.objects.get_or_create(
        name="casa-catchall-owner",
        defaults={"order": 0, "enabled": True},
    )
    workflow.order = 0
    workflow.enabled = True
    workflow.save()
    workflow.triggers.set([trigger])
    workflow.actions.set([action])
    print(
        f"[casa.catchall] {'created' if created else 'updated'}, owner={owner.username}"
    )
