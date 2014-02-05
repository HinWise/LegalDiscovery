
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

def blank_or_not_blank(request):
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
        
    try:
        show_progress = request.POST['show_progress']
        
    except (KeyError):
    
        show_progress='dont_show'
           
    try:
        save_id = request.POST['save_id']
        
    except (KeyError):
    
        save_id='NoId'
        
    try:
        success_message = request.POST['success_message']
        
    except (KeyError):
    
        success_message='' 
        
    try:
        blank_or_not_blank = request.POST['blank_or_not_blank']
        
    except (KeyError):
    
        blank_or_not_blank='NoChoice'
          
    the_user = request.user
    user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="TeamAuditors").exclude(name="Arabic")[0]
    
    user_profile = UserProfile.objects.get(user = the_user)
    
    if the_user.is_superuser == False and user_group.name != "Enersect_Berlin":
        
        return HttpResponseRedirect(reverse('enersectapp:main', args=()))
        
    sourcepdfs_list = SourcePdf.objects.none()
    count_blank_probable = "No Blank Probables Left"

    count_total = 0
    
    if blank_or_not_blank != "NoChoice" and blank_or_not_blank != "RollBack":
        #job1\scan1~2013_06_08_11_00_00_248.pdf
        if(save_id!="NoId"): 
        
            source_to_change = SourcePdf.objects.filter(id=save_id)[0]
            
            doctype_class = SourceDocType.objects.filter(name=blank_or_not_blank)[:1]
            
            if (len(doctype_class)>0):
                doctype_class=doctype_class[0]
            else:
                doctype_class = SourceDocType()
                doctype_class.name = blank_or_not_blank
                doctype_class.pretty_name = blank_or_not_blank
                doctype_class.save()
            
            source_to_change.document_type= blank_or_not_blank
            source_to_change.modified_document_type = doctype_class
            source_to_change.modification_doctype_date=datetime.datetime.now().replace(tzinfo=timezone.utc)
            source_to_change.modification_doctype_author=the_user
            source_to_change.save()
            
            if len(user_profile.modifiedsourcepdfs_blank_or_not_tool.filter(pk=source_to_change.pk))==0:
                user_profile.modifiedsourcepdfs_blank_or_not_tool.add(source_to_change)
                user_profile.save()
                
    
    #count_total = len(SourcePdf.objects.all())
    

    doctype_blankprobable = SourceDocType.objects.get(name="blank probable")
    sourcepdfs_list = SourcePdf.objects.filter(modified_document_type=doctype_blankprobable).values('id','modified_document_type__name','job_directory','filename').order_by()
    count_blank_probable = len(sourcepdfs_list)

    if (count_blank_probable>0):
         
        random_int = random.randrange(0,count_blank_probable,1)
        source_item = sourcepdfs_list[random_int]

    else:
        source_item = []
        
    chosen_item =  source_item
  
    
    if blank_or_not_blank == "RollBack":
        
        all_items = user_profile.modifiedsourcepdfs_blank_or_not_tool.all().order_by('-modification_doctype_date')
        length = len(all_items)
        last_item = all_items[0]
        blank_probable_type = SourceDocType.objects.get(name="blank probable")
        last_item.modified_document_type = blank_probable_type
        last_item.save()
        user_profile.modifiedsourcepdfs_blank_or_not_tool.remove(last_item)
        chosen_item = last_item
        
    
    count_this_user = len(user_profile.modifiedsourcepdfs_blank_or_not_tool.all())
    
    show_progress_user = 'Completed by you: '+str(count_this_user)
        
  
    if blank_or_not_blank != "NoChoice" and blank_or_not_blank != "RollBack":
  
        if blank_or_not_blank == "blank":
        
            success_message = "The previous document was saved as BLANK"
            
        else:
        
            type = blank_or_not_blank.upper()
            success_message = "The previous document was saved as "+type+" (NOT BLANK)"
    
  
    context = {'user_group':user_group.name,'success_message':success_message,
    'chosen_item':chosen_item,'the_user':the_user.username,
    'count_blank_probable':count_blank_probable,'count_total':count_total,'show_progress_user':show_progress_user}
    
    return render(request,'enersectapp/blank_or_not_blank.html',context)