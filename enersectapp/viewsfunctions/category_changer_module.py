
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


import random

def category_changer(request):

    the_user = request.user
    
    if not request.user.is_authenticated() or the_user.is_superuser == False :
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    try:
        save_mark = request.POST['save_mark']
        
    except (KeyError):
    
        save_mark='none'
        
    try:
        type1 = request.POST['type1']
        
    except (KeyError):
    
        type1='none'
        
    try:
        type2 = request.POST['type2']
        
    except (KeyError):
    
        type2='none'
        
    try:
        type3 = request.POST['type3']
        
    except (KeyError):
    
        type3='none'
      
    types_list = SourceDocType.objects.all().order_by('name','id')
    success_message = ""
    
    if save_mark == "delete_mark" and type3!="none":
    
        try:
            type3_doctype = SourceDocType.objects.filter(name=type3)[0]
        except:
            type3_doctype = ""
            
        if type3_doctype:    
            all_sources_type3 = SourcePdf.objects.filter(modified_document_type = type3_doctype)
            all_pdfs_type3 = PdfRecord.objects.filter(modified_document_type = type3_doctype)
        
            if len(all_sources_type3)==0 and len(all_pdfs_type3)==0:
                type3_doctype.delete()
        
        return HttpResponseRedirect(reverse('enersectapp:category_changer', args=()))
    
    if save_mark == "save_mark" and type1!="none" and type2 !="none":
    
        type1_doctype = SourceDocType.objects.filter(name=type1)[0]
        type2_doctype = SourceDocType.objects.filter(name=type2)[0]
            
        all_sources_type1 = SourcePdf.objects.filter(modified_document_type = type1_doctype)
        all_pdfs_type1 = PdfRecord.objects.filter(modified_document_type = type1_doctype)
        
        with transaction.commit_on_success():  
            for item in all_sources_type1:
                
                if item:
                    item.modified_document_type = type2_doctype
                    item.original_document_type_string = type1
                    item.save()
        
            for pdf in all_pdfs_type1:
                
                if pdf:
                    pdf.modified_document_type = type2_doctype
                    pdf.modified_doctype_from = type1
                    pdf.save()
        
 
        success_message = "Changed all documents with type "+type1+" to type "+type2
            

    context = {'types_list':types_list,'the_user':the_user,'success_message':success_message}
    #print "DonE!----------------23"
    return render(request,'enersectapp/category_changer.html',context)