from django.apps import AppConfig
from django.db.models.signals import m2m_changed, post_migrate, post_save


class CasaConfig(AppConfig):
    name = "casa"
    verbose_name = "Casa provisioning"

    def ready(self):
        from django.contrib.auth.models import User
        from documents.models import Correspondent, DocumentType, StoragePath, Tag

        from .catchall_workflow import on_user_created, provision_catchall_workflow
        from .groups import provision_groups
        from .orphan_guard import adopt_orphan
        from .superadmins import provision_extra_superadmins
        from .superuser_sync import sync_superuser

        # post_migrate fires on every boot, including when no migrations are
        # pending, so this is the reconcile path. Each handler filters on
        # sender.label == "documents" to run exactly once per migrate pass,
        # after the paperless tables exist.
        post_migrate.connect(provision_groups)
        post_migrate.connect(provision_extra_superadmins)
        post_migrate.connect(provision_catchall_workflow)

        # On an empty instance the owner does not exist yet at post_migrate
        # time, so the catch-all is wired on first login instead.
        post_save.connect(on_user_created, sender=User)

        # Auxiliary objects are created automatically during consumption and
        # no workflow assigns them an owner. Ownerless means visible to all.
        for model in (Tag, Correspondent, DocumentType, StoragePath):
            post_save.connect(adopt_orphan, sender=model)

        m2m_changed.connect(sync_superuser, sender=User.groups.through)
