from django.apps import AppConfig
from django.db.models.signals import m2m_changed, post_migrate, post_save


class CasaConfig(AppConfig):
    name = "casa"
    verbose_name = "Casa provisioning"

    def ready(self):
        from django.apps import apps as django_apps
        from django.contrib.auth.models import User
        from django.db import connection
        from django.db.utils import DatabaseError
        from documents.models import Correspondent, DocumentType, StoragePath, Tag

        from .catchall_workflow import on_user_created, provision_catchall_workflow
        from .groups import provision_groups
        from .orphan_guard import adopt_orphan
        from .superadmins import provision_extra_superadmins
        from .superuser_sync import sync_superuser

        # First boot: migrations run, post_migrate fires, handlers provision.
        # Each handler filters on the 'documents' app so it runs exactly once.
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

        # Subsequent boots: paperless does not invoke migrate when nothing is
        # pending, so post_migrate never fires and the handlers above would
        # not run again. Config changes (SSO_GROUP_*, the superadmin list)
        # only take effect through this path, so reconcile here as well.
        #
        # This deliberately writes to the database from ready(), which the
        # README otherwise forbids. The table check guards the pre-migrate
        # case; do not remove it.
        try:
            if "auth_user" not in connection.introspection.table_names():
                return
        except DatabaseError:
            # Database not reachable yet; post_migrate will cover this boot.
            return

        documents = django_apps.get_app_config("documents")
        provision_groups(documents)
        provision_extra_superadmins(documents)
        provision_catchall_workflow(documents)
