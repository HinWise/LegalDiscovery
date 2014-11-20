
import enersectapp

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db import connection
from django import db

from enersectapp.models import *

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response


from PyPDF2 import PdfFileWriter, PdfFileMerger, PdfFileReader
from urllib2 import Request, urlopen
from StringIO import StringIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import time
import tempfile
import pytz
from tzlocal import get_localzone

from django.db.models import Count

import json 


import gc
from django.views import generic
from django.utils import timezone
from datetime import timedelta
import datetime


import os
import shutil

import string
import random

from django.core.files.base import ContentFile
    
def download_emails_interface(request):

    the_user = request.user
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
        
    if len(the_user.groups.filter(name="Clients")) >0:
    
        user_type = "TeamLeader"
        
    elif the_user.is_superuser == True :
    
        user_type = "superuser"
        
    else:
    
        user_type = "user"

        
    if user_type != "superuser" and user_type != "Client":
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
        
    try:
        file_to_download = request.POST["selected_file_mark"]
    except:
        file_to_download = ""
    
    try:
        affidavit_action_mark = request.POST["affidavit_action_mark"]
    except:
        affidavit_action_mark = ""
    
    
    if affidavit_action_mark == "download_file_action" and file_to_download != "":
        download_emails(request,file_to_download)
    
    
    temp_documents = os.listdir('legaldiscoverytemp')
    console.log(os.path)
    console.log(os.listdir())
    all_documents.extend(temp_documents)
    
    all_documents = sorted(all_documents)
    
    context = {'user_type':user_type,'the_user':the_user,
                'all_documents':all_documents}
    
    return render(request,'enersectapp/download_emails.html',context)
    
    
def download_emails(request,file_to_download):

    the_user = request.user
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
        
    if len(the_user.groups.filter(name="Clients")) >0:
    
        user_type = "TeamLeader"
        
    elif the_user.is_superuser == True :
    
        user_type = "superuser"
        
    else:
    
        user_type = "user"

        
    if user_type != "superuser" and user_type != "Client":
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))

   
    file_to_download = str(file_to_download)
        

    string_to_return = file_to_download
    file_to_send = ContentFile(string_to_return)
    
    response     = HttpResponse(file_to_send,'application/x-gzip')
    response['Content-Length']      = file_to_send.size    
    response['Content-Disposition'] = 'attachment; filename='+file_to_download
    return response 
