from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView

from .models import Site
from authentication.mixins import GroupRequiredMixin
from centraspect import settings


class SitesListView(GroupRequiredMixin, LoginRequiredMixin, ListView):
    group_names = [settings.ACCOUNT_ADMIN_GROUP, ]
    template_name = 'admin/sites/all_sites.html'
    model = Site

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SitesListView, self).get_context_data(**kwargs)
        context['sites'] = Site.objects.get_all_active_for_account(account=self.request.user.account)
        return context
