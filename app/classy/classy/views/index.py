

# If user is authenticated redirect to home, otherwise redirect to the auth url of the keycloak server. Here the user chooses how to authenticate (IDIR or local keycloak account). Once authenticated they are redirected to /login_complete
#@csrf_protect
def index(request):
    if request.user.is_authenticated:
        return redirect('classy:home')

    auth_url = settings.OIDC_CLIENT.authorization_url(redirect_uri=os.getenv('REDIRECT_URI') + reverse('classy:login_complete'))#, scope='username email', state='alskdfjl;isiejf'
    return redirect(auth_url)   
	
def health(request):
    return HttpResponse(200)