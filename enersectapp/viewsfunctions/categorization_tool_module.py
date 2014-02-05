
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

def categorization_tool(request):
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    #Mode indicates if the Pdfs to categorize are taken from the "No Category" Pool on the Source Pdfs, the "Other" Pool on the Entries, or All Entries.
    
    try:
        mode = request.POST['mode']
        
    except (KeyError):
    
        mode='other_mode'
        
    try:
        show_progress = request.POST['show_progress']
        
    except (KeyError):
    
        show_progress='dont_show'
           
    try:
        save_id = request.POST['save_id']
        
    except (KeyError):
    
        save_id='NoId'
        
    try:
        doctype = request.POST['doctype']
        
    except (KeyError):
    
        doctype='NoDocType'
        
        
    the_user = request.user
    user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="TeamAuditors").exclude(name="Arabic")[0]
    user_profile = UserProfile.objects.get(user = the_user)
    
    if the_user.is_superuser == False and user_group.name != "Enersect_Berlin":
        
        return HttpResponseRedirect(reverse('enersectapp:main', args=()))
        
    
    sourcepdfs_list = SourcePdf.objects.none()
    count_uncategorized = "No Uncategorized in this Mode"
    count_other = "No Others in this Mode"
    count_total = 0
    
    types_list = SourceDocType.objects.exclude(name="other").exclude(name="recuperation").exclude(name="blank probable").order_by('name')
    
    if(doctype!="NoDocType"):
    
        doctype = doctype.lower()
        #Prevent having spaces after the name
        doctype = doctype.rstrip()
        
                    
        if doctype == "invoice/facture":
            doctype = "invoice"
            
        if doctype == "receipt/recu":
            doctype = "receipt"
        
        
    if mode == "uncategorized_mode":
        #job1\scan1~2013_06_08_11_00_00_248.pdf
        if(save_id!="NoId" and doctype!="NoDocType"): 
            source_to_change = SourcePdf.objects.filter(id=save_id)[0]
            
            doctype_class = SourceDocType.objects.filter(name=doctype)[:1]
            if (len(doctype_class)>0):
                doctype_class=doctype_class[0]
            else:
                doctype_class = SourceDocType()
                doctype_class.name = doctype
                doctype_class.pretty_name = doctype
                doctype_class.save()
            
            source_to_change.document_type=doctype
            source_to_change.modified_document_type = doctype_class
            source_to_change.modification_doctype_date=datetime.datetime.now().replace(tzinfo=timezone.utc)
            source_to_change.modification_doctype_author=the_user
            source_to_change.save()
            
            associated_pdfs = PdfRecord.objects.filter(sourcedoc_link = source_to_change)
            
            
            #Changes also the entries made from that Source Document
            if (len(associated_pdfs)>0):
                with transaction.commit_on_success():
                    for pdfrecord_to_change in associated_pdfs:
                        
                        pdfrecord_to_change.modified_doctype_from = doctype
                        pdfrecord_to_change.modified_document_type = doctype_class
                        pdfrecord_to_change.modified_doctype_date=datetime.datetime.now().replace(tzinfo=timezone.utc)
                        pdfrecord_to_change.modified_doctype_author=the_user
                        pdfrecord_to_change.save()
            
            if len(user_profile.modifiedsourcepdfs_categorization_tool.filter(pk=source_to_change.pk))==0:
                user_profile.modifiedsourcepdfs_categorization_tool.add(source_to_change)
                user_profile.save()
    
        #count_total = len(SourcePdf.objects.all())
        pdfrecords_list = PdfRecord.objects.none()
        doctype_uncategorized = SourceDocType.objects.get(name="uncategorized")
        sourcepdfs_list = SourcePdf.objects.filter(modified_document_type=doctype_uncategorized).values('id','modified_document_type__name','job_directory','filename').order_by()
        count_uncategorized = len(sourcepdfs_list)

        if (count_uncategorized>0):
         
            random_int = random.randrange(0,count_uncategorized,1)
            sourcepdfs_item = sourcepdfs_list[random_int]

        else:
            sourcepdfs_item = []
        
        chosen_item =  sourcepdfs_item
    
    
    elif mode == "other_mode":
    
        if(save_id!="NoId" and doctype!="NoDocType"): 
            pdfrecord_to_change = PdfRecord.objects.filter(id=save_id)[0]
            doctype_class = SourceDocType.objects.filter(name=doctype)[:1]
            if (len(doctype_class)>0):
                doctype_class=doctype_class[0]
            else:
                doctype_class = SourceDocType()
                doctype_class.name = doctype
                doctype_class.pretty_name = doctype
                doctype_class.save()
                
            pdfrecord_to_change.modified_doctype_from=doctype
            pdfrecord_to_change.modified_document_type = doctype_class
            pdfrecord_to_change.modified_doctype_date=datetime.datetime.now().replace(tzinfo=timezone.utc)
            pdfrecord_to_change.modified_doctype_author=the_user
            
            #Changes also the Source Document DocType, from which the entry was made
            
            pdfrecord_to_change.sourcedoc_link.original_document_type_string = doctype
            pdfrecord_to_change.sourcedoc_link.modified_document_type = doctype_class
            pdfrecord_to_change.sourcedoc_link.modification_doctype_date=datetime.datetime.now().replace(tzinfo=timezone.utc)
            pdfrecord_to_change.sourcedoc_link.modification_doctype_author=the_user
            pdfrecord_to_change.sourcedoc_link.save()
            pdfrecord_to_change.save()
            
            if len(user_profile.modifiedpdfs_categorization_tool.filter(pk=pdfrecord_to_change.pk))==0:
                user_profile.modifiedpdfs_categorization_tool.add(pdfrecord_to_change)
                user_profile.save()
    
        sourcepdfs_list = SourcePdf.objects.none()
        doctype_other = SourceDocType.objects.get(name="other")
        pdfrecords_list = PdfRecord.objects.filter(modified_document_type=doctype_other).values('id','modified_document_type__name','sourcedoc_link__job_directory','sourcedoc_link__filename').order_by()
        count_other = len(pdfrecords_list)
    
        if (count_other>0):
            random_int = random.randrange(0,count_other,1)
            pdfrecords_item = pdfrecords_list[random_int]
            
        else:
            pdfrecords_item = []
        
        chosen_item =  pdfrecords_item
    
    else:
        
        return HttpResponseRedirect(reverse('enersectapp:main', args=()))
  
    
    count_this_user = len(user_profile.modifiedsourcepdfs_categorization_tool.all())+ len(user_profile.modifiedpdfs_categorization_tool.all())
    show_progress_user = 'Completed by you: '+str(count_this_user)
    
  
    context = {'mode':mode,'user_group':user_group.name,'types_list':types_list,
    'chosen_item':chosen_item,'the_user':the_user.username,'count_other':count_other,
    'count_uncategorized':count_uncategorized,'count_total':count_total,'show_progress_user':show_progress_user}
    
    return render(request,'enersectapp/categorization_tool.html',context)