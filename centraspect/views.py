from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt

from . import messages


class LandingPage(TemplateView):
    template_name = 'landing.html'


@csrf_exempt
def return_invalid_token_response(request, *args, **kwargs):
    error_message = kwargs.pop('error_message') or None
    if error_message is None:
        error_message = messages.GENERIC_ERROR

    return JsonResponse(status=401, data={"Token Error": error_message})


@csrf_exempt
def return_token_expired_response(request, *args, **kwargs):
    error_message = kwargs.pop('error_message') or None
    if error_message is None:
        error_message = messages.AUTH_TOKEN_EXPIRED_ERROR

    return JsonResponse(status=401, data={"Token Expired": error_message})


