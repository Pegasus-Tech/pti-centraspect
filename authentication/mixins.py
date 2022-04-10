from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect


class GroupRequiredMixin:
    group_names = None

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if self.group_names is None:
            raise ImproperlyConfigured(f'{self.__class__.__name__} does not have group_name defined')

        groups = Group.objects.filter(name__in=self.group_names)

        if not groups.exists():
            raise ValueError(f'No group with name {self.group_names} found.')

        for gr in groups:
            if gr in user.groups.all():
                return super().dispatch(request, *args, **kwargs)

        return redirect('dashboard')
