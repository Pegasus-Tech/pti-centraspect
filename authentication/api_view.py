import json

from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Token
from centraspect import messages
from centraspect.decorators import token_required


@csrf_exempt
def get_auth_token(request):
    if request.method == 'POST':
        creds = json.loads(request.body)
        user = authenticate(username=creds['email'], password=creds['password'])

        if user is not None:
            token = Token.objects.get_or_create(user=user)[0]
            return JsonResponse(status=200,  data=token.to_json)
        else:
            return JsonResponse(status=400, data={"Credential Error", "Invalid Credentials Provided"}, safe=True)


@csrf_exempt
def refresh_auth_token(request):
    if request.method == "POST":
        data = json.loads(request.body)
        # TODO: validate the refresh token then refresh and then return the updated token response.

@csrf_exempt
@token_required
def access_this(request):
    return JsonResponse(status=200, data={"Hello": "World"})
