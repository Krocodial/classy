from ratelimit.decorators import ratelimit
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth import login
import os


from classy.views.common import helper



# If user is authenticated redirect to home, otherwise redirect to the auth url of the keycloak server. Here the user chooses how to authenticate (IDIR or local keycloak account). Once authenticated they are redirected to /login_complete
#@csrf_protect
def index(request):
    if request.user.is_authenticated:
        return HttpResponse(200)

    auth_url = settings.OIDC_CLIENT.authorization_url(redirect_uri=os.getenv('REDIRECT_URI') + reverse('classy:login'))#, scope='username email', state='alskdfjl;isiejf'
    return redirect(auth_url)   


# User is redirected here after authentication is complete via keycloak authentication server with a long, short-lived code. We exchange this code via an out-of-band REST call to the keycloak auth server for an access and refresh token. In the token is a list of permissions the user has, we check and set these via middleware. Once the token is verified we log the user in via a local session and give them a session cookie (they will never see the tokens so no risk of mishandling)
#@requires_csrf_token
@ratelimit(key='header:x-forwarded-for', rate=helper.custom_rate, block=True)
def login_complete(request):
    try:
        redirect_uri = os.getenv('REDIRECT_URI') +  reverse('classy:login')
        token = settings.OIDC_CLIENT.authorization_code(code=request.GET['code'], redirect_uri=redirect_uri)
        payload = settings.OIDC_CLIENT.decode_token(token['access_token'], settings.OIDC_CLIENT.certs()['keys'][0], options={"verify_signature": True, "verify_aud": True, "exp": True})
        request.session['access_token'] = token['access_token']
        request.session['refresh_token'] = token['refresh_token']
    except Exception as e:
        return HttpResponseForbidden('Invalid JWT token') 

    User = get_user_model()

    username = payload.get('sub')
    if username is None:
        return HttpResponseForbidden('Invalid payload')

    try:
        user, user_created = User.objects.get_or_create(username=username)
    except Exception as e:
        return HttpResponseForbidden('Error creating user') 

    if user_created:
        user.set_password(User.objects.make_random_password(length=40))
        user.email = payload.get('email')
        user.first_name = payload.get('name')
        user.last_name = payload.get('preferred_username')
        user.save()    
    elif user.email != payload.get('email'):
        user.email = payload.get('email')
        user.save()

    helper.role_checker(user, payload, request)

    if not user.is_active:
        return HttpResponseForbidden('Contact the appropriate party for permission. This access attempt has been logged.')
    login(request, user)
    return HttpResponse(200)
    
    
def health(request):
    return HttpResponse(200)
