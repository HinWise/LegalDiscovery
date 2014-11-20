
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
import tempfile
from django.core.servers.basehttp import FileWrapper,FileWrapperFixed
    
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
    
    else:
    
        all_documents = []
        
        temp_documents = os.listdir("app/ProjectFolder/nasolid_mail/")
        
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
        
    #path_file = "app/ProjectFolder/nasolid_mail/"+file_to_download
    path_file = "app/ProjectFolder/nasolid_mail/test.txt"
    
    wrapper = FileWrapper(file(path_file), "rb") 
    #FileWrapper(open(path_file, "rb"))
    
    string_to_return = file_to_download
    #file_opened = open("app/ProjectFolder/nasolid_mail/"+file_to_download, 'w')
    file_to_send = wrapper
    
    #response = HttpResponse(file_to_send,content_type='application/x-gzip')
    #response['Content-Length']      = file_to_send.size os.path.getsize(filename)    
    #response['Content-Disposition'] = 'attachment; filename=test.gz'
    
    response = HttpResponse(wrapper,content_type='text/plain')
    response['Content-Length'] = os.path.getsize(path_file)
    #response['Content-Length']      = file_to_send.size os.path.getsize(filename)  


    outputStream = StringIO()
    final_output = (FileWrapperFixed(file(path_file, 'rb')))
    final_output.write(outputStream)
    
    response = HttpResponse(mimetype="text/plain")

    response['Content-Disposition'] = 'attachment; filename="app/ProjectFolder/nasolid_mail/test.txt"'


    ##If .pdf instead, this line is necessary:
    response.write(outputStream.getvalue())
    
    if response: 
        return response
        
    else:
        raise Exception("FAIL!")
