from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from authentication.mixins import GroupRequiredMixin
from centraspect import settings


class AdminIndexView(GroupRequiredMixin, LoginRequiredMixin, TemplateView):
    group_names = [settings.ACCOUNT_ADMIN_GROUP]
    template_name = 'admin/index.html'
    