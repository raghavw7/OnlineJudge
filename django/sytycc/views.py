from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required()
def profile(request):

    # if request.user.is_authenticated():
    user = request.user
    return render(request, 'profile.html', {'user':user})