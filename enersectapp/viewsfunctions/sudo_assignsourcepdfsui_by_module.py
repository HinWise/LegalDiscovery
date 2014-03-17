
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

def sudo_assignsourcepdfsui_by_doctype_and_number(request):

    the_user = request.user
    
    if not request.user.is_authenticated() or the_user.is_superuser == False :
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    try:
        company_name = request.POST['company_name']
        
    except (KeyError):
    
        company_name='NoCompanyName'
      
    try:
        doctype_name = request.POST['doctype_name']
        
    except (KeyError):
    
        doctype_name='NoDocType'
     
    try:
        user_name = request.POST['user_name']
        
    except (KeyError):
    
        user_name='NoUserName'
     
    try:
        num_toassign = request.POST['num_toassign']
        
    except (KeyError):
    
        num_toassign='0'
    
    try:
        save_data = request.POST['save_data']
        
    except (KeyError):
    
        save_data='dont_save'
    
    success_message = ""
    
    none_user = User.objects.get(username="None")
    
    if user_name != "NoUserName":
    
        user_to_assign = User.objects.get(username=user_name)
        user_to_assign_profile = UserProfile.objects.get(user = user_to_assign )
        if user_to_assign_profile.assignation_locked != "locked" and save_data=="save_data":
            user_to_assign_profile.assignation_locked = "locked"
            user_to_assign_profile.save()
        
    else:
    
        user_to_assign = none_user
    
    num_toassign = int(num_toassign)
    
    company_names_list = Group.objects.exclude(name="INVENSIS").exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="TeamAuditors").exclude(name="Arabic").values_list('name',flat=True).distinct()
    doctype_names_list = []
    user_names_list = []

    number_follow_assign_criteria = 0
    number_docs_not_in_company = 0
    
    lot_number_list = SourcePdfToHandle.objects.exclude(assignedcompany__name="TestGroup").order_by().values_list('lot_number',flat=True).distinct()
                
    max_lotnum = int(max(lot_number_list))
    
    
    
    if company_name != "NoCompanyName":
        
        the_company = Group.objects.get(name=company_name)
        

        if doctype_name != "NoDocType":
        
            user_names_list = User.objects.filter(groups = the_company).exclude(groups__name ="TeamLeaders").values_list('username',flat=True).distinct()
        
            #Inside this If I will take up to the selected number of documents to assign
            #from the chosen Company and assign them to the chosen Company, to the helper
            #user "None", and mark them with a Lot Number equal to the maximum existing Lot Number + 1
            
            
            the_doctype =  SourceDocType.objects.get(name=doctype_name)
            
            if num_toassign !=0 and save_data=="save_data":

                docs_to_assign = SourcePdf.objects.exclude(assigndata__assignedcompany = the_company).filter(modified_document_type = the_doctype).order_by()[:num_toassign]
                
                with transaction.commit_on_success():
                    for source in docs_to_assign:
                        if source:
                             
                            tohandle = SourcePdfToHandle(assignedcompany=the_company,assigneduser=user_to_assign,lot_number=max_lotnum+1)
                            tohandle.save()
                            source.assigndata.add(tohandle)
                            source.save()

                    
                    max_lotnum = max_lotnum+1
                    if user_name != "NoUserName":
                        success_message = str(len(docs_to_assign)) + " Documents from " + doctype_name + " were assigned to " + company_name + ", User '"+ user_name +"' as Lot "+ str(max_lotnum) + "."
                    else:
                        success_message = str(len(docs_to_assign)) + " Documents from " + doctype_name + " were assigned to " + company_name + " as Lot "+ str(max_lotnum) + "."
                    
                    try:
                        new_lotnum = LotNumber.objects.get(lot_number = max_lotnum+1)
                    except:
                        new_lotnum = LotNumber(lot_number = max_lotnum+1)
                    
                    new_lotnum.save()
                    
                    group_profile = GroupProfile.objects.get(group = the_company)
                    group_profile.unique_lot_number_list.add(new_lotnum)
                    group_profile.save()
                    
            the_doctype =  SourceDocType.objects.get(name=doctype_name)
            
            docs_not_in_company = SourcePdf.objects.exclude(assigndata__assignedcompany = the_company).order_by()
            
            docs_in_doctype = docs_not_in_company.filter(modified_document_type = the_doctype).order_by()
            
            number_follow_assign_criteria = len(docs_in_doctype)
            
            number_docs_not_in_company = len(docs_not_in_company)
            
            doctype_names_list = docs_not_in_company.values_list('modified_document_type__name',flat=True).distinct()
            
        else:
            
            docs_not_in_company = SourcePdf.objects.exclude(assigndata__assignedcompany = the_company).order_by()
            
            number_follow_assign_criteria = 0
            number_docs_not_in_company = len(docs_not_in_company)
            
            
            doctype_names_list = docs_not_in_company.values_list('modified_document_type__name',flat=True).distinct()
            

    
    context = {'doctype_name':doctype_name,'company_name':company_name,'user_name':user_name,'success_message':success_message,
    'number_follow_assign_criteria':number_follow_assign_criteria,'number_docs_not_in_company':number_docs_not_in_company,
    'max_lotnum':max_lotnum,'company_names_list':company_names_list,'doctype_names_list':doctype_names_list,'user_names_list':user_names_list}
    
    return render(request,'enersectapp/sudo_assign_by_doctype_and_number.html',context)