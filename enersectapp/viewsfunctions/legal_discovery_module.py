
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db import connection

from enersectapp.models import *

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response

from pyPdf import PdfFileWriter, PdfFileReader
from urllib2 import Request, urlopen
from StringIO import StringIO


from django.views import generic
from django.utils import timezone
from datetime import timedelta
import datetime


import random

def legal_discovery(request):
    
    the_user = request.user
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
        
    if len(the_user.groups.filter(name="TeamLeaders")) >0:
    
        user_type = "TeamLeader"
        
    elif the_user.is_superuser == True :
    
        user_type = "superuser"
        
    else:
    
        user_type = "user"

        
    if user_type != "superuser" and user_type != "TeamLeader" and user_type != "Client":
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
        
        
    user_profile = UserProfile.objects.get(user = the_user)

    
    '''try:
        word_amount = request.POST['search_word_amount']
    except (KeyError):
        
        word_amount = ""'''
        
    
    final_entries = PdfRecord.objects.filter(audit_mark = "None").distinct()
    
    print "THIS FINAL ENTRIES ->" + str(len(final_entries))
    
    

    context = {'user_type':user_type,'the_user':the_user}
    
    return render(request,'enersectapp/legal_discovery.html',context)