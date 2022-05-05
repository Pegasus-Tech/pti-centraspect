from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect

from authentication.models import Token
from authentication.utils import parse_auth_token
from centraspect import messages
from centraspect.views import return_invalid_token_response, return_token_expired_response


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


class TokenRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        print(f"Request Headers :: {request.headers}")
        headers = request.headers
        auth_token = parse_auth_token(headers.get('X-Centra-Auth-Token') or None)

        print(f"Got Auth Token :: {auth_token}")

        # first check if we even get an auth token
        if auth_token is None:  # return error to prompt token request
            kwargs.update({"error_message": messages.NO_AUTH_TOKEN_PROVIDED_ERROR})
            return return_invalid_token_response(request, *args, **kwargs)

        else:  # find the related token object and validate the expiration of the current token - refresh as needed
            token_obj = Token.objects.filter(auth_token=auth_token) or None

            if token_obj is None:  # return error to prompt login
                kwargs.update({"error_message": messages.INVALID_AUTH_TOKEN_ERROR})
                return return_invalid_token_response(request, *args, **kwargs)

            else:  # Everything is good, return the response with the authed user
                if not Token.objects.token_expired(auth_token=token_obj.get().auth_token):
                    kwargs['authed_user'] = token_obj.get().user
                    return super().dispatch(request, *args, **kwargs)
                else:
                    kwargs.update({"error_message": messages.AUTH_TOKEN_EXPIRED_ERROR})
                    return return_token_expired_response(request, *args, **kwargs)
