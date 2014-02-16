
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

from django.db.models import Count


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

    legaldiscovery_templates_names_list = user_profile.created_legaldiscovery_templates.all().values_list('name').distinct()
    
    '''try:
        word_amount = request.POST['search_word_amount']
    except (KeyError):
        
        word_amount = ""'''
        
    
    final_entries = PdfRecord.objects.filter(audit_mark = "None").distinct()
    
    used_document_types_dictionary_list = final_entries.values('modified_document_type__name').order_by().annotate(count=Count('id')).order_by('-count')
    
    
    document_types_list_dictionaries = []
    
    with transaction.commit_on_success():
        for item in used_document_types_dictionary_list:
        
            doctype = SourceDocType.objects.get(name = item['modified_document_type__name'] )
            
            new_element = {}
            new_element.update({"name":str(doctype.name)})
            new_element.update({"count":item['count']})
            new_element.update({"min_show":1})
            new_element.update({"max_show":item['count']})
            new_element.update({"min_selected":1})
            new_element.update({"max_selected":item['count']})
            
            new_element.update({"id":doctype.pk})
            

            extraction_fields_list = doctype.extraction_fields.all().order_by('-importance').values_list('real_field_name',flat=True)
            clean_extraction_fields_list = []
            
            for field in extraction_fields_list:
                
                new_extraction_marker = {}
                
                new_extraction_marker.update({"name":str(field)})
                new_extraction_marker.update({"checked":"checked"})
                new_extraction_marker.update({"sorting":"default"})
                
                clean_extraction_fields_list.append(new_extraction_marker)
            
            new_element.update({"extraction_fields":clean_extraction_fields_list})
            
            document_types_list_dictionaries.append(new_element)
            
    
    total_doctypes_list = SourceDocType.objects.all()
    

    context = {'user_type':user_type,'the_user':the_user,'document_types_list_dictionaries':document_types_list_dictionaries,
                'legaldiscovery_templates_names_list':legaldiscovery_templates_names_list}
    
    return render(request,'enersectapp/legal_discovery.html',context)