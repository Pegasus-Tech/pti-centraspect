import json

from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Token
from centraspect import messages
from centraspect.decorators import token_required
from centraspect.exceptions import InvalidTokenError


@csrf_exempt
def get_auth_token(request):
    if request.method == 'POST':
        creds = json.loads(request.body)

        try:
            user = authenticate(username=creds['email'], password=creds['password'])
            print(f'User :: {user}')
            if user is not None:
                token = Token.objects.get_or_create(user=user)[0]
                return JsonResponse(status=200,  data=token.to_json)
            else:
                return JsonResponse(status=400, data={"Credential Error": "Invalid Credentials Provided"})
        except Exception as e:
            print(e)


@csrf_exempt
def refresh_auth_token(request):
    if request.method == "POST":
        data = json.loads(request.body)
        refresh_token = data.get('refresh_token') or None
        token_obj = Token.objects.filter(refresh_token=refresh_token) or None

        if refresh_token is None:
            return JsonResponse(status=400, data={'error_message': messages.NO_REFRESH_TOKEN_PROVIDED_ERROR})

        else:
            try:
                token = token_obj.get()
                token.refresh_auth_token(provided_refresh=refresh_token)
                return JsonResponse(status=200,  data=token.to_json)

            except InvalidTokenError:
                return JsonResponse(status=400, data={"error_message": messages.INVALID_REFRESH_TOKEN_ERROR})


# TODO: remove method after testing with Mobile App
@csrf_exempt
@token_required
def access_this(request):
    return JsonResponse(status=200, data={"Hello": "World"})
