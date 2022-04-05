from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission


GROUPS = ['Viewer', 'User', 'Inspector', 'Account Admin', 'Superuser']
CUSTOM_MODELS = ['inspection_items', 'inspection_forms', 'inspections', 'authentication']

VIEWER_PERMS = []
USER_PERMS = []
INSPECTOR_PERMS = []
ACCOUNT_ADMIN_PERMS = []


class Command(BaseCommand):
    help = 'Creates custom groups and permissions for Centraspect'

    def handle(self, *args, **options):

        try:
            for grp in GROUPS:
                group, created = Group.objects.get_or_create(name=grp)

            perms = Permission.objects.all()
            # view_perm_labels(perms)
            build_view_permissions(perms)
            build_user_permissions(perms)
            build_inspector_permissions(perms)
            build_account_admin_permissions(perms)
        except Exception as e:
            raise CommandError("Error creating custom groups and permissions.", e)


def view_perm_labels(perms):
    for perm in perms:
        if perm.content_type.app_label in CUSTOM_MODELS:
            print(f"Permission :: {perm.codename} | {perm.name}")


def build_view_permissions(perms):
    group = Group.objects.get(name='Viewer')
    for perm in perms:
        if perm.content_type.app_label in CUSTOM_MODELS:
            if 'view' in perm.codename:
                VIEWER_PERMS.append(perm)

    for vp in VIEWER_PERMS:
        group.permissions.add(vp)

    group.save()
    print("######### Viewer Permissions #########")
    view_perm_labels(group.permissions.all())
    print()


def build_user_permissions(perms):
    group = Group.objects.get(name='User')
    for perm in perms:
        if perm.content_type.app_label in CUSTOM_MODELS:
            if 'view' in perm.codename or 'assigned' in perm.codename:
                USER_PERMS.append(perm)

    for vp in USER_PERMS:
        group.permissions.add(vp)

    group.save()
    print("######### User Permissions #########")
    view_perm_labels(group.permissions.all())
    print()


def build_inspector_permissions(perms):
    group = Group.objects.get(name='Inspector')
    for perm in perms:
        if perm.content_type.app_label in CUSTOM_MODELS:
            if 'view' in perm.codename or 'assigned' in perm.codename:
                INSPECTOR_PERMS.append(perm)
            if perm.content_type.app_label != 'authentication' and 'add' in perm.codename:
                INSPECTOR_PERMS.append(perm)

    for vp in INSPECTOR_PERMS:
        group.permissions.add(vp)

    print("######### Inspector Permissions #########")
    view_perm_labels(group.permissions.all())
    print()


def build_account_admin_permissions(perms):
    group = Group.objects.get(name='Account Admin')
    for perm in perms:
        if perm.content_type.app_label in CUSTOM_MODELS:
            ACCOUNT_ADMIN_PERMS.append(perm)

    for vp in ACCOUNT_ADMIN_PERMS:
        group.permissions.add(vp)

    print("######### Account Admin Permissions #########")
    view_perm_labels(group.permissions.all())
    print()
