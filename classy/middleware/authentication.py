from django.contrib.auth import logout
from django.conf import settings
from jose.exceptions import ExpiredSignatureError, JWTError
from ..helper import role_checker

def authentication_middleware(get_response):
   
    def middleware(request):
        if request.user.is_authenticated:

            access = request.session['access_token']
            refresh = request.session['refresh_token']
            
            
            try:
                settings.OIDC_CLIENT.decode_token(access, settings.OIDC_CLIENT.certs()['keys'][0])
                settings.OIDC_CLIENT.userinfo(request.session['access_token'])

            except ExpiredSignatureError: 
                try:
                    settings.OIDC_CLIENT.decode_token(refresh, settings.OIDC_CLIENT.certs()['keys'][0])
                    token = settings.OIDC_CLIENT.refresh_token(request.session['refresh_token'])
                    request.session['access_token'] = token['access_token']
                    request.session['refresh_token'] = token['refresh_token']

                    payload = settings.OIDC_CLIENT.decode_token(token['access_token'], settings.OIDC_CLIENT.certs()['keys'][0])
                    role_checker(request.user, payload, request)

                except:
                    logout(request)
            except:
                logout(request)

        response = get_response(request)

        return response 
    return middleware
