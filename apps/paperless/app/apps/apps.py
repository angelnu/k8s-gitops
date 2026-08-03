from django.apps import AppConfig
from django.db.models.signals import m2m_changed, post_migrate, post_save


class CasaConfig(AppConfig):
    name = "casa"
    verbose_name = "Casa provisioning"

    def ready(self):
        from django.contrib.auth.models import User

        from .catchall_workflow import on_user_created, provision_catchall_workflow
        from .groups import provision_groups
        from .superadmins import provision_extra_superadmins
        from .superuser_sync import sync_superuser

        # post_migrate fires once per migrated app; each handler filters on
        # the 'documents' app itself so it runs exactly once, after the
        # paperless tables exist.
        post_migrate.connect(provision_groups)
        post_migrate.connect(provision_extra_superadmins)
        post_migrate.connect(provision_catchall_workflow)

        # On an empty instance the owner does not exist yet at post_migrate
        # time, so the catch-all is wired on first login instead.
        post_save.connect(on_user_created, sender=User)

        m2m_changed.connect(sync_superuser, sender=User.groups.through)
