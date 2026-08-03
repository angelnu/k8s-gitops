import os


def _csv(name, default=""):
    return set(
        filter(None, (v.strip() for v in os.environ.get(name, default).split(",")))
    )


# Group names, driven by the SSO group claim.
SSO_GROUP_READER = os.environ.get("SSO_GROUP_READER", "casa_readers")
SSO_GROUP_WRITER = os.environ.get("SSO_GROUP_WRITER", "casa_editors")
SSO_GROUP_ADMIN = os.environ.get("SSO_GROUP_ADMIN", "casa_admins")

# Per-instance superadmins that do not warrant their own authentik group.
EXTRA_SUPERADMINS = _csv("PAPERLESS_EXTRA_SUPERADMIN_USERS")

# Local break-glass accounts the reconcile must never touch.
PROTECTED = _csv("PAPERLESS_PROTECTED_USERS", "admin")

# Owner for anything that would otherwise be created ownerless.
INSTANCE_OWNER = os.environ.get("PAPERLESS_INSTANCE_OWNER", "")

# Every user needs these or the frontend 403s on /api/ui_settings/.
BASE_PERMS = [
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

SPEC = {
    SSO_GROUP_READER: {"models": DOC_MODELS, "actions": ["view"]},
    SSO_GROUP_WRITER: {
        "models": DOC_MODELS,
        "actions": ["view", "add", "change", "delete"],
    },
    # Admins get their reach from is_superuser, not model permissions.
    SSO_GROUP_ADMIN: None,
}
