
from enersectapp.models import *

from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response

def app_login(request):
  
    logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                #return HttpResponseRedirect('enersectapp:main')
                return HttpResponseRedirect(reverse('enersectapp:main', args=()))
                #return reverse('enersectapp:main', args=())
    return render_to_response('enersectapp/app_login.html', context_instance=RequestContext(request))