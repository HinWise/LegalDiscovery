
from enersectapp.models import *

import json
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response

def show_transaction(request,path_filename):
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    the_user = request.user
   

    context = {"the_user":the_user,'transaction_dict':transaction_dict}
    return render(request,'enersectapp/show_transaction.html',context)