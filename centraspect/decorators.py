from functools import wraps

from centraspect import messages
from authentication.models import Token
from centraspect.exceptions import InvalidTokenError
from centraspect.views import return_invalid_token_response

import json


def token_required(view_func):
    """ Decorator for validating auth tokens for api requests """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        print(f"Request Body :: {json.loads(request.body)}")
        if request.body is not None and request.body != b'':
            data = json.loads(request.body)
            auth_token = data.get('auth_token') or None
            refresh_token = data.get('refresh_token') or None

            # first check if we even get an auth token
            if auth_token is None:  # return error to prompt token request
                kwargs.update({"error_message": messages.NO_AUTH_TOKEN_PROVIDED_ERROR})
                return return_invalid_token_response(request, *args, **kwargs)

            else:  # find the related token object and validate the expiration of the current token - refresh as needed
                token_obj = Token.objects.filter(auth_token=auth_token) or None

                if token_obj is None:  # return error to prompt login
                    kwargs.update({"error_message": messages.INVALID_AUTH_TOKEN_ERROR})
                    return return_invalid_token_response(request, *args, **kwargs)

                else:
                    if not Token.objects.token_expired(auth_token=token_obj.get().auth_token):
                        return view_func(request, *args, **kwargs)

                    else:
                        if refresh_token is None:  # return error to prompt login
                            kwargs.update({"error_message": messages.NO_REFRESH_TOKEN_PROVIDED_ERROR})
                            return return_invalid_token_response(request, *args, **kwargs)

                        else:  # refresh the auth token and move on
                            try:
                                # TODO: Return a refresh error and make the client refresh the token
                                token_obj.get().refresh_auth_token(provided_refresh=refresh_token)
                                return view_func(request, *args, **kwargs)

                            except InvalidTokenError:  # return to login page
                                kwargs.update({"error_message": messages.INVALID_REFRESH_TOKEN_ERROR})
                                return return_invalid_token_response(request, *args, **kwargs)

        else:
            kwargs.update({"error_message": messages.NO_AUTH_TOKEN_PROVIDED_ERROR})
            return return_invalid_token_response(request, *args, **kwargs)

    return wrapper
