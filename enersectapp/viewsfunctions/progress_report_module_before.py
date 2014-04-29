
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

import re
import json,csv

def progress_report(request):

    the_user = request.user
    
    if not request.user.is_authenticated() or (the_user.is_superuser == False and the_user.username != "JamesTL") :
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    try:
        export_mark = request.POST['export_mark']
        
    except (KeyError):
    
        export_mark='none'
    
    super_group = Group.objects.get(name="NathanTeam")
    test_group = Group.objects.get(name="TestGroup")
    invensis_group = Group.objects.get(name="INVENSIS")
    
    #Number of total Source Documents
    
    source_documents_all = SourcePdf.objects.all().values('filename','modified_document_type').distinct()
    
    total_source_documents = len(source_documents_all)
    
    #Number of Source Documents that have a category other than "Uncategorized" or "Other"
    
    total_with_doctype = len(source_documents_all.exclude(modified_document_type__name="uncategorized").exclude(modified_document_type__name="other"))
    
    
    # Number of total documents entered
    
    total_pdf_entered_list = PdfRecord.objects.exclude(audit_mark="duplicatemarked_reentered").exclude(audit_mark="auditmarked_confirmed_reassignment").exclude(ocrrecord_link__OcrByCompany=test_group).exclude(ocrrecord_link__OcrByCompany=invensis_group).exclude(ocrrecord_link__OcrByCompany=super_group).values('ocrrecord_link','modified_document_type','sourcedoc_link','status','audit_mark').order_by().distinct()
    
    total_pdf_entered = len(total_pdf_entered_list)
    
    #Groups and names of the Groups
    
    #Documents entered by each Group
    

    company_names_list = total_pdf_entered_list.values_list('ocrrecord_link__OcrByCompany__name',flat=True).order_by().distinct()
    
    company_names_and_values_list = []
    
    for item in company_names_list:
    
        name = item
        count = len(total_pdf_entered_list.filter(ocrrecord_link__OcrByCompany__name = name).values('ocrrecord_link').order_by().distinct())
        dictionary_item = {}
        dictionary_item['name'] = name
        dictionary_item['count'] = count
        company_names_and_values_list.append(dictionary_item)

    
    #List of Document Types entered and how many of each
    
    document_types_list = total_pdf_entered_list.values_list('modified_document_type__name',flat=True).distinct()
    
    # Number of each Doctype entered
 
    document_types_names_and_values_list = []
    
    for item in document_types_list:
    
        name = item
        count = len(total_pdf_entered_list.filter(modified_document_type__name = name).values('modified_document_type','id').order_by().distinct())
        dictionary_item = {}
        dictionary_item['name'] = name
        dictionary_item['count'] = count
        document_types_names_and_values_list.append(dictionary_item)
    
    
    # Number of total documents linked

    
    total_linked_documents = len(total_pdf_entered_list.filter(status = "pdf_linked"))
   
   
   
    # Number of total documents rejected
    # Number of entries divided by Country
    
    if export_mark == "export_csv":
    
        date = datetime.datetime.now().strftime("%d_%m_%Y")
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="progress_report_'+date+'".csv"'

        writer = csv.writer(response)
        writer.writerow(['               ', 'Total Number Of:', '               '])
        writer.writerow(['Source Documents', total_source_documents, '               '])
        writer.writerow(['Documents With an Identified Document Type', total_with_doctype, '               '])
        writer.writerow(['               ','               ','               '])
        writer.writerow(['Documents Entries Made', total_pdf_entered, '               '])
        writer.writerow(['Documents Entries Linked to a Record', total_linked_documents, '               '])
        writer.writerow(['               ','               ','               '])
        for item in company_names_and_values_list:
            writer.writerow(['Entries made by '+item['name'], item['count'], '               '])
        writer.writerow(['               ','               ','               '])    
        for item in document_types_names_and_values_list:
            writer.writerow(['Entries with Document Type '+item['name'], item['count'], '               '])
        
        
        return response
        #return HttpResponseRedirect(reverse('enersectapp:progress_report', args=()))  
    
    else:
    
        context = {'total_source_documents':total_source_documents,'total_with_doctype':total_with_doctype,
        'total_pdf_entered':total_pdf_entered,'company_names_and_values_list':company_names_and_values_list,
        'document_types_names_and_values_list':document_types_names_and_values_list,
        'total_linked_documents':total_linked_documents,'the_user':the_user}
        #print "DonE!----------------23"
        return render(request,'enersectapp/progress_report.html',context)