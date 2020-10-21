from django.contrib.auth.decorators import login_required

@login_required
def tutorial(request):
    return HttpResponse('coming soon...')
    if request.user.is_staff:
        return render(request, 'classy/tutorial.html')
    if request.user.is_authenticated:
        return render(request, 'classy/base_tutorial.html')
